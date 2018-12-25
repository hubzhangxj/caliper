#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
import os
import re
import stat
import shutil
import glob
import sys
from pwd import getpwnam
try:
    import caliper.common as common
except ImportError:
    import common

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import server.setup

CURRENT_PATH = os.path.dirname(sys.modules[__name__].__file__)
# CALIPER_TMP_DIR = os.path.join('/home', os.environ['SUDO_USER'], 'caliper_output')
# CALIPER_REPORT_HOME = CALIPER_TMP_DIR
# CALIPER_DIR = CURRENT_PATH

def _combine_dicts(list_dicts):
    result_dict = {}
    for d in list_dicts:
        for k in d:
            result_dict[k] = d[k]
    return result_dict


def get_packages():
    return (server.setup.get_packages())


def get_package_dirs():
    return _combine_dicts(
            [server.setup.get_package_dirs()]
            )


def recursive_file_permissions(path, mode, uid=-1, gid=-1):
    '''
    Recursively updates file permissions on a given path.
    UID and GID default to -1, and mode is required
    '''
    for item in glob.glob(path + '/*'):
        if os.path.isdir(item):
            os.chown(item, uid, gid)
            recursive_file_permissions(os.path.join(path, item), mode, uid, gid)
        else:
            try:
                os.chown(os.path.join(path, item), uid, gid)
                os.chmod(os.path.join(path, item), mode)
            except:
                print('File permissions on {0} not updated due to error.'.format(os.path.join(path, item)))

def run():
    try:
        caliper_data_dir = os.path.join('/home', os.environ['SUDO_USER'], '.caliper')
        caliper_output = os.path.join('/home', os.environ['SUDO_USER'], 'caliper_output')
    except:
        caliper_data_dir = os.path.join(os.environ['HOME'], '.caliper')
        caliper_output = os.path.join(os.environ['HOME'], 'caliper_output')
    caliper_tmp_dir = os.path.join(caliper_data_dir, 'benchmarks')
    caliper_configuration = os.path.join(caliper_output,'configuration')
    caliper_config_file = os.path.join(caliper_configuration,'config')
    project_config_path = os.path.join(re.split('caliper',os.getcwd())[0],'caliper')
    if os.path.exists(caliper_tmp_dir):
        shutil.rmtree(caliper_tmp_dir)

    if os.path.exists(caliper_config_file):
        shutil.rmtree(caliper_config_file)

    shutil.copytree(
            os.path.join(project_config_path, 'config'), caliper_config_file
            )
    shutil.copystat(
            os.path.join(project_config_path, 'config'), caliper_config_file
    )

    shutil.copytree(
        os.path.join(project_config_path, 'benchmarks'),
        caliper_tmp_dir
    )
    shutil.copystat(
        os.path.join(project_config_path, 'benchmarks'),
        caliper_tmp_dir
    )
    os.chmod(caliper_data_dir, stat.S_IRWXO + stat.S_IRWXU)
    os.chmod(caliper_tmp_dir, stat.S_IRWXO + stat.S_IRWXU)
    setup(
            name='caliper',
            version=common.VERSION,
            description='A test suite for automatically running on different\
                devices, and compare the test results',
            package_dir=get_package_dirs(),
            package_data=server.setup.get_package_data(),
            packages=get_packages(),
            data_files=server.setup.get_data_files(),
            scripts=server.setup.get_scripts(),
            url='http://github.com/open-estuary/caliper',
            maintainer="open-estuary",
            install_requires=['pyYAML',
                       #'poster==0.8.1',
                     #'openpyxl==2.4.9',
                 #'cryptography==2.1.4',
                  #'setuptools==38.4.0',
                     #'paramiko==2.4.0',
                    #'ansible==2.4.2.0'
                 ]
            )
    try:
        os.chown(caliper_output, getpwnam(os.environ['SUDO_USER']).pw_uid,-1)
        recursive_file_permissions(path=caliper_output,mode=0775,uid=getpwnam(os.environ['SUDO_USER']).pw_uid,gid=-1)
    except:
        os.chown(caliper_output, getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid, -1)
        recursive_file_permissions(path=caliper_output, mode=0775,
                                   uid=getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid, gid=-1)

    if os.path.exists('caliper.egg-info'):
        shutil.rmtree('caliper.egg-info')
    #if os.path.exists('dist'):
    #    shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # get_packages()

if __name__ == "__main__":
    run()
