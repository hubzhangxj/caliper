#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from caliper.server.shared import error, settings
import ConfigParser
from caliper.server.hosts import ssh_host
from caliper.server.shared import caliper_path

DEFAULT_FOLLOW_PATH = '/var/log/kern.log'
DEFAULT_PATTERNS_PATH = 'console_patterns'
SSH_ENGINE = settings.settings.get_value('Common', 'ssh_engine')
_started_hostnames = set()
settings_path_root = os.path.join(
                        caliper_path.config_files.config_dir, 'project_config.cfg')

def get_remote_host():
    '''
    get test host
    :return: host info
    '''
    cf = ConfigParser.ConfigParser()
    cf.read(settings_path_root)
    sections = cf.sections()
    opts = cf.options(sections[0])[0].split(' ')
    client_ip = opts[0]
    user_list = cf.get(sections[0], cf.options(sections[0])[0])
    user = user_list.split(' ')[0]
    port = 22
    password = user_list.split('"')[1]
    remote_host = create_host(client_ip, user, password, port)
    return remote_host

def create_host(hostname, ssh_user, ssh_pass, ssh_port):
    """auto_monitor=True, follow_paths=None, pattern_paths=None,
    netconsole=False,"""
    # here, ssh_user, ssh_pass and ssh_port are injected in he namespace
    # pylint: disable=E0602
    args = {}
    args['user'] = ssh_user
    args['password'] = ssh_pass
    args['port'] = ssh_port
    args['profile'] = ''

    # by fault, assume we use SSH support
    if SSH_ENGINE == "paramiko":
        from caliper.server.hosts import paramiko_host
        classes = [paramiko_host.ParamokoHost]
    if SSH_ENGINE == 'raw_ssh':
        # ssh_host.AsyncSSHMixin
        classes = [ssh_host.SSHHost, ssh_host.AsyncSSHMixin]
    else:
        raise error.AutoError("Unknown SSH engine %s. Please verify the value"
                               " of the configuration key 'ssh_engine' on the"
                               " .ini file " % SSH_ENGINE)
    # create a custom host class for this machine and return an instance of it
    host_class = type("%s_host" % hostname, tuple(classes), {})
    host_instance = host_class(hostname, **args)

    if hostname not in _started_hostnames:
        host_instance.job_start()
        _started_hostnames.add(hostname)

    return host_instance
