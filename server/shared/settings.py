#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   15/01/07 19:21:42
#   Desc    :
#

import os
import subprocess
import logging
import yaml
import getpass
import ConfigParser
from caliper.server.shared import error
from caliper.server.shared import caliper_path


class SettingsError(error.AutoError):
    pass


class SettingsValueError(SettingsError):
    pass

settings_filename = 'project_config.cfg'
shadow_config_filename = 'shadow_config.cfg'

settings_path_root = os.path.join(
                        caliper_path.config_files.config_dir,
                        settings_filename)
config_in_root = os.path.exists(settings_path_root)

# need to change
if config_in_root:
    DEFAULT_CONFIG_FILE = settings_path_root
    RUNNING_STAND_ALONE_CLIENT = False
else:
    DEFAULT_CONFIG_FILE = None
    RUNNING_STAND_ALONE_CLIENT = False

class Settings(object):
    _NO_DEFAULT_SPECIFIED = object()

    config = None
    config_file = DEFAULT_CONFIG_FILE
    running_stand_alone_client = RUNNING_STAND_ALONE_CLIENT

    def check_stand_alone_client_run(self):
        return self.running_stand_alone_client

    def set_config_files(self, config_file=DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.config = self.parse_config_file()

    def _handle_no_value(self, section, key, default):
        if default is self._NO_DEFAULT_SPECIFIED:
            msg = ("Value '%s' not found in section '%s'" % (key, section))
            raise SettingsError(msg)
        else:
            return default

    def get_section_values(self, sections):
        """
        Return a config parser object containing a single section of the
        global configuration, that can be written to a file object.

        :param
        section: Tuple with sections we want to turn into a config
                        parser
        :return: ConfigParser() onject containing all the contents of
                        sections.
        """
        self._ensure_config_parsed()

        if isinstance(sections, str):
            sections = [sections]
        cfgparser = ConfigParser.ConfigParser()
        for section in sections:
            cfgparser.add_section(section)
            for option, value in self.config.items(section):
                cfgparser.set(section, option, value)
        return cfgparser

    def get_value(self, section, key, type=str, default=_NO_DEFAULT_SPECIFIED,
                    allow_blank=False):
        self._ensure_config_parsed()

        try:
            val = self.config.get(section, key)
        except ConfigParser.Error:
            return self._handle_no_value(section, key, default)

        if not val.strip() and not allow_blank:
            return self._handle_no_value(section, key, default)

        return self._convert_value(key, section, val, type)

    def override_value(self, section, key, new_value):
        """
        Override a value from the config file with a new value.
        """
        self._ensure_config_parsed()
        self.config.set(section, key, new_value)

    def reset_values(self):
        """
        Reset all values to those found in the config files (undoes all
        overrides).
        """
        self.parse_config_file()

    def _ensure_config_parsed(self):
        if self.config is None:
            self.parse_config_file()

    def merge_configs(self, shadow_config):
        # overwrite whats in config with whats in shadow_config
        sections = shadow_config.sections()
        for section in sections:
            # add the section if needed
            if not self.config.has_section(section):
                self.config.add_section(section)

            # now run through all options and set them
            options = shadow_config.options(section)
            for option in options:
                val = shadow_config.get(section, option)
                self.config.set(section, option, val)

    def parse_config_file(self):
        self.config = ConfigParser.ConfigParser()
        if self.config_file and os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise SettingsError('%s not found' % (self.config_file))

    # the values pulled from ini are strings
    # try to convert them to other types if needed.
    def _convert_value(self, key, section, value, value_type):
        sval = value.strip()

        if len(sval) == 0:
            if value_type == str:
                return
            elif value_type == bool:
                return False
            elif value_type == int:
                return 0
            elif value_type == float:
                return 0.0
            elif value_type == list:
                return []
            else:
                return None

        if value_type == bool:
            if sval.lower() == "false":
                return False
            else:
                return True

        if value_type == list:
            return [val.strip() for val in sval.split('.')]

        try:
            conv_val = value_type(sval)
            return conv_val
        except Exception:
            msg = ("Could not convert %s value in section %s to type %s" %
                    (key, section, value_type))
            raise SettingsValueError(msg)

    def read_config(self):
        '''
        :return: tool list and run case list
        '''
        config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
        fp = open(config_files, 'r')
        tool_list = []
        run_case_list = []
        case_list = yaml.load(fp.read())
        for dimension in case_list:
            for i in range(len(case_list[dimension])):
                for tool in case_list[dimension][i]:
                    for case in case_list[dimension][i][tool]:
                        if case_list[dimension][i][tool][case][0] == 'enable':
                            tool_list.append(tool)
                            run_case_list.append(case)
        sections = list(set(tool_list))
        return sections, run_case_list

    def get_config(self, option):
        '''
        :return: tool list and run case list
        '''
        config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
        fp = open(config_files, 'r')
        tool_list = []
        run_case_list = []
        case_list = yaml.load(fp.read())
        dimension_list = case_list.keys()
        tool_dic = {}
        for key, value in case_list.items():
            for va in value:
                for toolkey, toolvalue in va.items():
                    tool_dic[toolkey] = []
                    for casekey, casevalue in toolvalue.items():
                        tool_dic[toolkey].append(casekey)
        sections = []
        if option != 'all':
            if option in dimension_list:
                for i in range(len(case_list[option])):
                    for tool in case_list[option][i]:
                        for case in case_list[option][i][tool]:
                            tool_list.append(tool)
                            run_case_list.append(case)
                sections = list(set(tool_list))
            else:
                if option in tool_dic:
                    sections.append(option)
                    run_case_list = tool_dic[option]
                else:
                    run_case_list.append(option)
                    for tool in tool_dic:
                        if option in tool_dic[tool]:
                            sections.append(tool)
        else:
            sections, run_case_list = self.read_config()
        return sections, run_case_list

    def get_sections(self, dimension_list):
        all_sections = []
        config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
        fp = open(config_files, 'r')
        run_case_list = []
        case_list = yaml.load(fp.read())
        cf = ConfigParser.ConfigParser()
        cf.read(DEFAULT_CONFIG_FILE)
        devices = cf.options('FastTest')
        for device in devices:
            tool_list = yaml.load(cf.get('FastTest', device))
            all_sections = all_sections + tool_list
        sections = list(set(all_sections))
        for section in sections:
            for dimension in dimension_list:
                for i in range(len(case_list[dimension])):
                    try:
                        for case in case_list[dimension][i][section]:
                            run_case_list.append(case)
                    except:
                        pass
        return sections, run_case_list

    def get_run_sections(self, c_option, dimension_list, option):
        if c_option == 1:
            sections, run_case_list = self.get_sections(dimension_list)
        else:
            if 'all' in option:
                sections, run_case_list = self.get_config('all')
            else:
                sections, run_case_list = self.get_config(option)
        return sections, run_case_list

    def push_ssh_key(self):
        '''
        use ansible push ssh key to test host
        :return: 
        '''
        TEST_CASE_DIR = caliper_path.config_files.config_dir
        ssh_key_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa.pub')
        if not os.path.exists(ssh_key_path):
            os.system("ssh-keygen -t rsa -P '' -f '%s/.ssh/id_rsa'" % os.environ['HOME'])
        try:
            logging.info('Begining to push ssh key for the test host')
            os.chdir(TEST_CASE_DIR)
            cf = ConfigParser.ConfigParser()
            cf.read(DEFAULT_CONFIG_FILE)
            sections = cf.sections()
            for section in sections:
                if 'Device' not in section:
                    continue
                subprocess.call('ansible-playbook -i project_config.cfg push_sshkey.yml -e hosts=%s -u %s' % (
                section, getpass.getuser()), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as e:
            logging.debug(e)
            logging.info('push ssh key fail')
            pass

# insure the class is a singleton. Now the symbol settings will point to the
# one and only one instance pof the class
settings = Settings()
