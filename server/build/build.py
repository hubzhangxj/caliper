#!/usr/bin/python

import os
import subprocess
import re
import shutil
import logging
import yaml
import sys
import signal
import time
from pwd import getpwnam
import json
import getpass
import threading

try:
    import caliper.common as common
except ImportError:
    import common

import caliper.server.utils as server_utils
import caliper.server.shared.utils as client_utils
from caliper.server.shared import error
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as FOLDER
from caliper.server.run.run import get_sections

CALIPER_DIR = caliper_path.CALIPER_DIR
GEN_DIR = caliper_path.GEN_DIR
WS_GEN_DIR = os.path.join(FOLDER.workspace,'binary')
TEST_CASE_DIR = caliper_path.config_files.config_dir
BUILD_MAPPING_DIR = os.path.join(GEN_DIR,'build_mapping')
BUILD_MAPPING_FILE = BUILD_MAPPING_DIR
# SPV A unique folder name based on the date and time is created in /tmp so
# that multiple instance of caliper can run.
currentProcess = [0,os.getpid()]

signal_ingored = [signal.SIGINT,signal.SIGTERM,signal.SIGALRM,signal.SIGHUP]
original_sigint = [None]*len(signal_ingored)

class build_tool_thread(threading.Thread):
    def __init__(self, target_arch, host, sections, clear):
        threading.Thread.__init__(self)
        """
        target_arch means to build the caliper for the special arch
        sections mean build for tools
        """
        self.host = host
        self.sections = sections
        self.target_arch = target_arch
        self.clear = clear

    def run(self):
        global GEN_DIR, BUILD_MAPPING_FILE, BUILD_MAPPING_DIR
        GEN_DIR = caliper_path.GEN_DIR

        if self.target_arch:
            arch = self.target_arch
        else:
            arch = 'x86_64'
        # get the config file
        case_file = os.path.join(TEST_CASE_DIR, 'cases_config.json')
        fp = open(case_file, 'r')
        case_list = json.load(fp)
        BUILD_MAPPING_DIR = os.path.join(BUILD_MAPPING_DIR, arch)
        if not os.path.exists(BUILD_MAPPING_DIR):
            try:
                os.makedirs(BUILD_MAPPING_DIR)
            except:
                pass

        # set_signals()
        # check and delete those binaries if it is already built if -c is used
        if self.clear:
            logging.info("=" * 55)
            logging.info("WARNING: Please wait, dont run any other instance of caliper")
            for section in self.sections:
                BUILD_MAPPING_FILE = os.path.join(BUILD_MAPPING_DIR, section + '.yaml')
                with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
                    fp = open(BUILD_MAPPING_FILE)
                    dic = yaml.load(fp)
                    fp.close()
                    if type(dic) != dict:
                        dic = {}
                    if section in dic.keys():
                        for file in dic[section]['binaries']:
                            try:
                                shutil.rmtree(file)
                            except:
                                pass
                        dic[section]['binaries'] = []
                        dic[section]['ProcessID'] = 0
                    fp = open(BUILD_MAPPING_FILE, 'w')
                    fp.write(yaml.dump(dic, default_flow_style=False))
                    fp.close()
            logging.info("It is safe to run caliper now")
            logging.info("=" * 55)

        for section in self.sections:
            BUILD = 0
            BUILD_MAPPING_FILE = os.path.join(BUILD_MAPPING_DIR, section + '.yaml')
            reset_binary_mapping()

            try:
                # Lock the file and modify it if this is the first process which is building the tool
                with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
                    fp = open(BUILD_MAPPING_FILE)
                    dic = yaml.load(fp)
                    if type(dic) != dict:
                        dic = {}
                    fp.close()
                    if section not in dic.keys():
                        dic[section] = {}
                        dic[section]['binaries'] = []
                        dic[section]['ProcessID'] = os.getpid()
                        BUILD = 1
                    fp = open(BUILD_MAPPING_FILE, 'w')
                    fp.write(yaml.dump(dic, default_flow_style=False))
                    fp.close()

                # checking if binary field is empty, empty means that the previous build is a failure
                if not dic[section]['binaries']:
                    BUILD = 1
            except Exception as e:
                logging.debug(e)
                sys.exit(1)

            BUILD = 1
            if BUILD == 1:
                logging.info("=" * 55)
                logging.info("Building %s" % section)
                build_dir = os.path.join(caliper_path.BENCHS_DIR, section, 'tests')
                build_config = os.path.join(TEST_CASE_DIR, 'hosts')
                log_name = "%s.log" % section
                log_file = os.path.join('/tmp', log_name)
                if not os.path.exists(build_dir):
                    download_section(section)
                os.chdir(build_dir)
                try:
                    if self.host != '':
                        result = subprocess.call(
                            'ansible-playbook -i %s site.yml --extra-vars "hosts=%s" -u %s>> %s 2>&1'
                            % (build_config, self.host, getpass.getuser(), log_file), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
                    else:
                        result = subprocess.call(
                            'ansible-playbook -i %s site.yml --extra-vars "hosts=Device" -u %s>> %s 2>&1'
                            % (build_config, getpass.getuser(), log_file), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
                except Exception as e:
                    result = e
                for k in range(len(case_list['network'])):
                    if section in case_list['network'][k]:
                        try:
                            subprocess.Popen(
                                'ansible-playbook -i %s runserver.yml -u %s' % (build_config, getpass.getuser()),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        except Exception as e:
                            pass
                if result:
                    logging.info("Building %s Failed" % section)
                    logging.info("=" * 55)
                    record_log(log_file, arch, 0)
                else:
                    logging.info("Building %s Successful" % section)
                    logging.info("=" * 55)
                    record_log(log_file, arch, 1)

        # reset_signals()
        return 0

def download_section(section):
    section_path = os.path.join(caliper_path.BENCHS_DIR, section)
    if not os.path.exists(section_path):
        try:
            logging.debug('Download %s from ansible-galaxy' % section)
            result = subprocess.call(
                'ansible-galaxy install --roles-path %s %s.%s'
                % (caliper_path.BENCHS_DIR, caliper_path.ansible_galaxy_name, section), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if os.path.exists(os.path.join(caliper_path.BENCHS_DIR, '%s.%s' % (caliper_path.ansible_galaxy_name, section))):
                shutil.copytree(
                    os.path.join(caliper_path.BENCHS_DIR, '%s.%s' % (caliper_path.ansible_galaxy_name, section)),
                    os.path.join(caliper_path.BENCHS_DIR, section)
                )
                shutil.rmtree(os.path.join(caliper_path.BENCHS_DIR, '%s.%s'%(caliper_path.ansible_galaxy_name,section)))
        except Exception,e:
            logging.info(e)
            pass


def copy_dic(src,dest,skip):
    try:
        for section in src.keys():
            if section not in dest.keys():
                dest[section] = src[section]
    except :
        pass

def reset_binary_mapping():
    global currentProcess

    with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
        fp = open(BUILD_MAPPING_FILE)
        dic = yaml.load(fp)
        fp.close()
        try:
            for section in dic.keys():
                if dic[section]['ProcessID'] in currentProcess:
                    if not dic[section]['binaries']:
                        del dic[section]
                    else:
                        dic[section]['ProcessID'] = 0
        except Exception as e:
            logging.debug(e)
            pass
        fp = open(BUILD_MAPPING_FILE,'w')
        fp.write(yaml.dump(dic, default_flow_style=False))
        fp.close()

def exit_gracefully():
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    global original_sigint
    global signal_ingored
    global BUILD_MAPPING_FILE
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], original_sigint[i])
    try:
        reset_binary_mapping()
    except Exception as e:
        logging.error(e)
    sys.exit(1)

    # restore the exit gracefully handler here
    # signal.signal(signal.SIGINT, exit_gracefully)


def set_signals():
    global original_sigint
    global signal_ingored
    for i in range(len(signal_ingored)):
        original_sigint[i] = signal.getsignal(signal_ingored[i])
        signal.signal(signal_ingored[i], exit_gracefully)

def reset_signals():
    global original_sigint
    global signal_ingored
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], signal.SIG_DFL)


def git(*args):
    return subprocess.check_call(['git'] + list(args))


def svn(*args):
    return subprocess.check_call(['svn'] + list(args))


def insert_content_to_file(filename, index, value):
    """
    insert the content to the index lines
    :param filename: the file will be modified
    :param index: the location eill added the value
    :param value: the content will be added
    """
    f = open(filename, "r")
    contents = f.readlines()
    f.close()

    contents.insert(index, value)

    f = open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

def getAllFilesRecursive(root):
    files = [os.path.join(root, f) for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    for d in dirs:
        files_in_d = getAllFilesRecursive(os.path.join(root, d))
        if files_in_d:
            for f in files_in_d:
                files.append(os.path.join(root, f))
    return files

def record_log(log_file, arch, succeed_flag):
    build_log_dir = FOLDER.build_dir
    main_build_dir = os.path.join(caliper_path.BUILD_LOGS, arch)
    if not os.path.exists(main_build_dir):
        os.makedirs(main_build_dir)
        os.chown(main_build_dir, getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid, -1)
    new_name_pre = log_file.split('/')[-1].split('.')[0] + '_' + arch
    pwd = os.getcwd()
    os.chdir(build_log_dir)
    subprocess.call("rm -fr %s*" % new_name_pre, shell=True)
    os.chdir(pwd)

    if (succeed_flag == 1):
        new_log_name = new_name_pre + '.suc'
    else:
        new_log_name = new_name_pre + '.fail'
        
    try:
        shutil.move(log_file, build_log_dir)
        current_file = os.path.join(FOLDER.build_dir, log_file.split("/")[-1])
        new_log_name = os.path.join(FOLDER.build_dir, new_log_name)
        os.rename(current_file, new_log_name)
        pwd = os.getcwd()
        os.chdir(main_build_dir)
        subprocess.call("rm -fr %s*" % new_name_pre, shell=True)
        os.chdir(pwd)
        shutil.copy(new_log_name,main_build_dir)
    except Exception, e:
        raise e


def create_folder(folder, mode=0755):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    try:
        os.mkdir(folder, mode)
    except OSError:
        os.makedirs(folder, mode)

def build_for_target(test_node, target, g_option, f_option, clear, sections):
    #f_option is set if -f is used
    # Create the temperory build folders

    if f_option == 0:
        if os.path.exists(FOLDER.caliper_log_file):
            os.remove(FOLDER.caliper_log_file)
        if os.path.exists(FOLDER.summary_file):
            os.remove(FOLDER.summary_file)
    if not os.path.exists(FOLDER.build_dir):
        create_folder(FOLDER.build_dir)
    if not os.path.exists(FOLDER.exec_dir):
        create_folder(FOLDER.exec_dir)
    if not os.path.exists(FOLDER.results_dir):
        create_folder(FOLDER.results_dir)
    if not os.path.exists(FOLDER.yaml_dir):
        create_folder(FOLDER.yaml_dir)
    if not os.path.exists(FOLDER.html_dir):
        create_folder(FOLDER.html_dir)

    # This call assign target_arch with target architecture. Call
    # "get_host_arch" looks to be confusing :(
    target_arch = server_utils.get_host_arch(target)

    try:
        host_arch = server_utils.get_local_machine_arch()
    except Exception, e:
        logging.debug(" Error in get_local_machine_arch()")
        raise e

    logging.info(" ")
    logging.info(" Local Host Arch : %s" % host_arch)
    logging.info(" Target Arch : %s" % target_arch)
    logging.info(" Caliper reports and logs are stored : %s" % FOLDER.workspace)
    logging.info(" ")

    try:
        dic = {}
        # Build all caliper benchmarks for the target architecture
        if g_option == 1:
            # concurrent build
            dic = get_sections()
        else:
            dic[test_node] = sections
        thread_list = []
        for device in dic:
            run_test = build_tool_thread(target_arch, device, dic[device], clear)
            run_test.start()
            time.sleep(1)
            thread_list.append(run_test)
        for thread in thread_list:
            thread.join()
        result = 0
    except Exception:
        result = 1
    else:
        if result:
            return result

    # Copy generated binaries to target machine
    # result = copy_gen_to_target(target, target_arch)
    return result


def copy_gen_to_target(target, target_arch):
    try:
        result = target.run("test -d caliper", ignore_status=True)
    except error.ServRunError, e:
        raise
    else:
        if not result.exit_status:
            target.run("cd caliper; rm -fr *; cd")
        else:
            target.run("rm -fr caliper; mkdir caliper")
        target.run("cd caliper;  mkdir -p binary")
        remote_pwd = target.run("pwd").stdout
        remote_pwd = remote_pwd.split("\n")[0]
        remote_caliper_dir = os.path.join(remote_pwd, "caliper")
        remote_gen_dir = os.path.join(remote_caliper_dir, "binary",
                                        target_arch)
        send_file_relative = ['server', 'common.py',  '__init__.py']
        send_files = [os.path.join(CALIPER_DIR, i) for i in
                send_file_relative]
        send_gen_files = os.path.join(GEN_DIR, target_arch)

        for i in range(0, len(send_files)):
            try:
                target.send_file(send_files[i], remote_caliper_dir)
            except Exception, e:
                logging.info("There is error when coping files to remote %s"
                                % target.ip)
                logging.info(e)
                raise
        target.send_file(send_gen_files, remote_gen_dir)
        logging.info("finished the scp caliper to the remote host")
        return 0

def copy_gen_to_server(target, path):
    try:
        result = target.run("test -d caliper_server", ignore_status=True)
    except error.ServRunError, e:
        raise
    else:
        if result.exit_status:
            target.run("mkdir -p caliper_server")

        remote_pwd = target.run("pwd").stdout
        remote_pwd = remote_pwd.split("\n")[0]
        remote_caliper_dir = os.path.join(remote_pwd, "caliper_server")
        try:
            target.send_file(path, remote_caliper_dir)
        except Exception, e:
            logging.info("There is error when coping files to remote %s"
                                % target.ip)
            logging.info(e)
            raise
        logging.info("finished the scp server script to the remote host")
        return 0

