#!/usr/bin/env python

import os
import sys
import time
import shutil
import re
import logging
import datetime
import subprocess
import ConfigParser
import yaml
import threading
try:
    import common
except ImportError:
    import caliper.common as common
from caliper.server import crash_handle
from caliper.server.shared import error
from caliper.server import utils as server_utils
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder


def get_sections():
    dic = {}
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(caliper_path.config_files.config_dir, 'hosts'))
    devices = cf.options('fasttest')
    for device in devices:
        tool_list = yaml.load(cf.get('fasttest', device))
        dic[device] = tool_list
    return dic

class run_case_thread(threading.Thread):
    def __init__(self, host, sections, run_case_list, num):
        threading.Thread.__init__(self)
        self.host = host
        self.sections = sections
        self.run_case_list = run_case_list
        self.num = num

    def run(self):
        config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
        fp = open(config_files, 'r')
        # get the test cases defined files
        for section in self.sections:
            common.print_format()
            logging.info("Running %s" % section)
            bench = os.path.join(caliper_path.BENCHS_DIR, section, 'defaults')
            run_case_list = []
            if self.run_case_list == '':
                case_list = yaml.load(fp.read())
                for dimension in case_list:
                    for i in range(len(case_list[dimension])):
                        try:
                            for case in case_list[dimension][i][section]:
                                run_case_list.append(case)
                        except:
                            pass
            else:
                run_case_list = self.run_case_list
            try:
                # On some platforms, swapoff and swapon command is not able to execute.
                # So this function has been commented
                result = self.run_all_cases(bench, section, run_case_list)
            except Exception, e:
                logging.info(e)
                logging.info("Running %s Exception" % section)
                crash_handle.main()
                common.print_format()
            else:
                logging.info("Running %s Finished" % section)
        return 0

    def run_all_cases(self, kind_bench, bench_name, run_case_list):
        """
        function: run one benchmark which was selected in the configuration files
        """
        try:
            # get the abspath, which is filename of run config for the benchmark
            bench_conf_file = os.path.join(kind_bench, 'main.yml')
            # get the config sections for the benchmrk
            pf = open(bench_conf_file, 'r')
            values = yaml.load(pf.read())
            sections_run = values[bench_name].keys()
        except AttributeError as e:
            raise AttributeError
        except Exception:
            raise
        logging.debug("the sections to run are: %s" % sections_run)
        if not os.path.exists(Folder.exec_dir):
            os.mkdir(Folder.exec_dir)
        log_bench = os.path.join(Folder.exec_dir, bench_name)
        logfile = log_bench + "_output.log"
        tmp_log_file = log_bench + "_output_tmp.log"
        if os.path.exists(logfile):
            os.remove(logfile)

        starttime = datetime.datetime.now()
        if os.path.exists(Folder.caliper_log_file):
            sections = bench_name + " EXECUTION"
            fp = open(Folder.caliper_log_file, "r")
            f = fp.readlines()
            fp.close()
            op = open(Folder.caliper_log_file, "w")
            for line in f:
                if not (sections in line):
                    op.write(line)
            op.close()
        result = subprocess.call("echo '$$ %s EXECUTION START: %s' >> %s"
                                 % (bench_name,
                                    str(starttime)[:19],
                                    Folder.caliper_log_file),
                                 shell=True)
        # for each command in run config file, read the config for the benchmark
        for section in sections_run:
            if section in run_case_list:
                if self.num == 0:
                    config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
                    fp = open(config_files, 'r')
                    case_list = yaml.load(fp.read())
                    for dimension in case_list:
                        for i in range(len(case_list[dimension])):
                            for tool in case_list[dimension][i]:
                                for case in case_list[dimension][i][tool]:
                                    if case == section:
                                        self.num = case_list[dimension][i][tool][case][-1]
                flag = 0

                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
                # run the command of the benchmarks

                try:
                    for j in range(int(self.num)):
                        flag = self.run_client_command(section, tmp_log_file, bench_name)
                except Exception, e:
                    logging.info(e)
                    crash_handle.main()
                    server_utils.file_copy(logfile, tmp_log_file, 'a+')
                    if os.path.exists(tmp_log_file):
                        os.remove(tmp_log_file)

                    run_flag = server_utils.get_fault_tolerance_config(
                        'fault_tolerance', 'run_error_continue')
                    if run_flag == 1:
                        continue
                    else:
                        return result
                else:
                    server_utils.file_copy(logfile, tmp_log_file, 'a+')
                    if flag != 1:
                        logging.info("There is wrong when running the command \"%s\""
                                     % section)

                        if os.path.exists(tmp_log_file):
                            os.remove(tmp_log_file)
                        crash_handle.main()

                        run_flag = server_utils.get_fault_tolerance_config(
                            'fault_tolerance', 'run_error_continue')
                        if run_flag == 1:
                            return result
                    if os.path.exists(tmp_log_file):
                        os.remove(tmp_log_file)
            else:
                continue

            endtime = datetime.datetime.now()
            subprocess.call("echo '$$ %s EXECUTION STOP: %s' >> %s"
                            % (section, str(endtime)[:19],
                               Folder.caliper_log_file), shell=True)
            subprocess.call("echo '$$ %s EXECUTION DURATION %s Seconds'>>%s"
                            % (section,
                               (endtime - starttime).seconds,
                               Folder.caliper_log_file), shell=True)


    def run_client_command(self, cmd_sec_name, tmp_logfile, bench_name):
        fp = open(tmp_logfile, "a+")
        start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd_sec_name
        fp.write(start_log)
        fp.write("<<<BEGIN TEST>>>\n")
        tags = "[test: " + cmd_sec_name + "]\n"
        fp.write(tags)
        logs = "log: " + cmd_sec_name + "\n"
        fp.write(logs)
        fp.close()
        start = time.time()
        flag = 0
        logging.debug("the client running command is %s" % cmd_sec_name)

        try:
            logging.debug("begining to execute the command of %s on remote host"
                          % cmd_sec_name)
            fp = open(tmp_logfile, "a+")
            logging.debug("client command in localhost is: %s" % cmd_sec_name)
            # FIXME: update code for this condition
            [out, returncode] = self.run_commands(bench_name, cmd_sec_name)
            fp.close()
            server_utils.file_copy(tmp_logfile, '/tmp/%s_output.log' % bench_name, 'a+')
        except error.ServRunError, e:
            fp = open(tmp_logfile, "a+")
            fp.write("[status]: FAIL\n")
            sys.stdout.write(e)
            flag = -1
            fp.close()
        else:
            fp = open(tmp_logfile, "a+")
            if not returncode:
                fp.write("[status]: PASS\n")
                flag = 1
            else:
                fp.write("[status]: FAIL\n")
                flag = 0
            fp.close()
        fp = open(tmp_logfile, "a+")
        end = time.time()
        interval = end - start
        fp.write("Time in Seconds: %.3fs\n" % interval)
        if not re.search('redis', bench_name):
            fp.write("<<<END>>>\n")
            fp.write("%%%%%% test_end %%%%%%\n\n")
        fp.close()
        return flag

    def run_commands(self, bench_name, cmd_sec_name):
        returncode = -1
        output = ''
        pwd = os.getcwd()
        try:
            # the commands is multiple lines, and was included by Quotation
            try:
                logging.debug("the actual commands running in local is: %s"
                              % cmd_sec_name)
                test_case_dir = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'tests')
                cmd_sec_name_tmp_file = os.path.join(Folder.workspace, Folder.name, cmd_sec_name +'_tmp.log')
                subprocess.call("echo '$$ %s RUN START' >> %s"
                                % (cmd_sec_name, cmd_sec_name_tmp_file),shell=True)
                os.chdir(test_case_dir)
                result = subprocess.call(
                    'ansible-playbook -i %s %s.yml --extra-vars "hosts=%s" -u root>> %s 2>&1' %
                    (os.path.join(caliper_path.config_files.config_dir, 'hosts'), cmd_sec_name, self.host, cmd_sec_name_tmp_file), stdout=subprocess.PIPE, shell=True)
                subprocess.call("echo '$$ %s RUN STOP' >> %s"
                                % (cmd_sec_name, cmd_sec_name_tmp_file), shell=True)
                subprocess.call("echo '==================================' >> %s"
                                % (cmd_sec_name_tmp_file), shell=True)
                server_utils.file_copy(Folder.caliper_run_log_file, cmd_sec_name_tmp_file, 'a+')
                if os.path.exists(cmd_sec_name_tmp_file):
                    os.remove(cmd_sec_name_tmp_file)
            except error.CmdError, e:
                raise error.ServRunError(e.args[0], e.args[1])
        except Exception, e:
            logging.debug(e)
        else:
            if result:
                returncode = result
            else:
                returncode = 0
            try:
                output = result
            except Exception:
                output = result
        os.chdir(pwd)
        return [output, returncode]

def run_caliper_tests(test_node, f_option, g_option, sections, run_case_list, num):
    # f_option =1 if -f is used
    if f_option == 1:
        if not os.path.exists(Folder.exec_dir):
            os.mkdir(Folder.exec_dir)
    else:
        if os.path.exists(Folder.exec_dir):
            shutil.rmtree(Folder.exec_dir)
        os.mkdir(Folder.exec_dir)
    if not os.path.exists(Folder.results_dir):
        os.mkdir(Folder.results_dir)
    if not os.path.exists(Folder.yaml_dir):
        os.mkdir(Folder.yaml_dir)
    if not os.path.exists(Folder.html_dir):
        os.mkdir(Folder.html_dir)

    flag = 0
    try:
        dic = {}
        logging.debug("beginnig to run the test cases")
        if g_option == 1:
            # concurrent run
            dic = get_sections()
        else:
            dic[test_node] = sections
        thread_list = []
        for device in dic:
            run_test = run_case_thread(device, dic[device], run_case_list, num)
            run_test.start()
            thread_list.append(run_test)
        for thread in thread_list:
            thread.join()
    except error.CmdError:
        logging.info("There is wrong in running benchmarks")
        flag = 1
    return flag