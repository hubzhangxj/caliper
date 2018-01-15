#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
import datetime
import shutil
import ConfigParser

def judge_caliper_installed():
    try:
        output = subprocess.Popen('which caliper', shell=True,
                stdout=subprocess.PIPE)
    except Exception:
        return 0
    else:
        if output.stdout.readlines():
            return 1
        else:
            return 0

CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
CALIPER_DIR = os.path.abspath(os.path.join(CURRENT_PATH, '..', '..'))

caliper_output = os.path.join(os.environ['HOME'], 'caliper_output', 'configuration')
caliper_config_file = os.path.join(caliper_output,'config')
TIMP_STAMP = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")

# FETCHING THE TARGET HOST NAME AND ARCH FOR CREATING THE WORKSPACE
def ConfigValue(path=None,section=None,key=None,action='get',value=None):
    config = ConfigParser.ConfigParser()
    config.read(path)
    if action == 'get':
        return config.get(section, key)
    else:
        return config.set(section,key,value)
cf = ConfigParser.ConfigParser()
config_file_path = os.path.join(caliper_config_file, 'project_config.cfg')
cf.read(config_file_path)
sections = cf.sections()
opts = cf.options(sections[0])[0].split(' ')
client_ip = opts[0]
user_list = cf.get(sections[0], cf.options(sections[0])[0])
client_user = user_list.split(' ')[0]
sudo_password = user_list.split('"')[-2]

try:
    platForm_name = ConfigValue(path=os.path.join(caliper_output,'config','project_config.cfg'), section='Common', key='testtask_name',action='get')
except:
    platForm_name = str(client_user)
else:
    if not platForm_name:
        platForm_name = client_user

try:
    ansible_galaxy_name = ConfigValue(path=os.path.join(caliper_output,'config','project_config.cfg'), section='Common', key='ansible_galaxy',action='get')
except:
    ansible_galaxy_name = ''

WORKSPACE = os.path.join(os.environ['HOME'], 'caliper_output', str(platForm_name) + '_WS_' + TIMP_STAMP)
# intermediate = 0

def create_folder(folder, mode=0755):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    try:
        os.mkdir(folder, mode)
    except OSError:
        os.makedirs(folder, mode)


if not judge_caliper_installed():
    # This means caliper is not installed and execution will be local.
    # Output folders are created with in the local directory structure.
    # This will allow multi instance of caliper to execute.
    # fixme CALIPER_REPORT_HOME ??? replace it with CALIPER_REPORT_HOME
    CALIPER_REPORT_HOME = os.path.join(CALIPER_DIR, 'caliper_output')
    BENCHS_DIR = os.path.join(CALIPER_DIR, 'benchmarks')
else:
    # This means that the caliper is already installed. Only instance can
    # execute as the updatation of the results will happen under
    # ~/home/user/caliper_workspace
    CALIPER_TMP_DIR = os.path.join(os.environ['HOME'], 'caliper_output')
    CALIPER_REPORT_HOME = CALIPER_TMP_DIR
    BENCHS_DIR = os.path.join(os.environ['HOME'], '.caliper', 'benchmarks')

BUILD_TIME = os.path.join(CALIPER_DIR,"server","build","building_timing.yaml")
TMP_DIR = os.path.join('/tmp', 'caliper.tmp'+ "_" + TIMP_STAMP)
GEN_DIR = os.path.join(CALIPER_REPORT_HOME, 'binary')
BUILD_LOGS = os.path.join(os.environ['HOME'],'.caliper_build_logs')

class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst


class Folder(Singleton):
    workspace = ''
    name = ''
    build_dir = ''
    exec_dir = ''
    results_dir = ''
    caliper_log_file = ''
    summary_file = ''
    yaml_dir = ''

    def __init__(self, folder=""):
        if folder:
            self.workspace = folder
        if not folder:
            self.workspace = WORKSPACE
        self.name = os.path.join('output')

    def set_up_path(self):
        self.workspace = os.path.join(os.path.join(os.environ['HOME'], 'caliper_output', self.workspace))
        self.name = os.path.join('output')
        self.build_dir = os.path.join(self.workspace, self.name,
                                            'caliper_build')
        self.exec_dir = os.path.join(self.workspace, self.name,
                                            'caliper_exec')
        self.results_dir = os.path.join(self.workspace, self.name,
                                            'results')
        self.caliper_log_file = os.path.join(self.workspace, self.name,
                                            'caliper_exe.log')
        self.caliper_run_log_file = os.path.join(self.workspace, self.name,
                                             'caliper_run.log')
        self.summary_file = os.path.join(self.workspace, self.name,
                                            'results_summary.log')
        self.final_parser = os.path.join(self.workspace, self.name,'final_parsing_logs.yaml')
        self.yaml_dir = os.path.join(self.results_dir, 'yaml')
        self.json_dir = os.path.join(self.results_dir, 'json')
        self.hardwareinfo = os.path.join(self.json_dir, 'hardwareinfo.json')
        self.caliper_message_file = os.path.join(self.workspace, self.name,
                                                 'test_message.txt')
        self.project_config = os.path.join(self.workspace, 'config', 'project_config.cfg')

folder_ope = Folder()
folder_ope.set_up_path()


class ConfigFile(Singleton):
    tests_cfg_dir = ''
    config_dir = ''
    name = ''

    def __init__(self, folder=""):
        if folder:
            self.name = os.path.abspath(folder)
        else:
            if judge_caliper_installed():
                self.name = caliper_output
            else:
                self.name = CALIPER_DIR

    def setup_path(self):
        self.config_dir = os.path.join(self.name, 'config')

config_files = ConfigFile()
config_files.setup_path()

def create_dir():

    if not os.path.exists(folder_ope.build_dir):
        create_folder(folder_ope.build_dir)
    if not os.path.exists(folder_ope.exec_dir):
        create_folder(folder_ope.exec_dir)
    if not os.path.exists(folder_ope.results_dir):
        create_folder(folder_ope.results_dir)
    if not os.path.exists(folder_ope.yaml_dir):
        create_folder(folder_ope.yaml_dir)
