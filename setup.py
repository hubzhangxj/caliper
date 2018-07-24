#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
import os
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
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

def _combine_dicts(list_dicts):
    result_dict = {}
    for d in list_dicts:
        for k in d:
            result_dict[k] = d[k]
    return result_dict

def get_data_files():
    return [((os.path.join(os.environ['HOME'], 'caliper_output/configuration/config')), ['config/ansible.cfg','config/cases_config.json','config/project_config.cfg','config/push_sshkey.yml'])]    


def get_packages():
    return ['caliper.server.build',
            'caliper.server.score',
            'caliper.server.hosts',
            'caliper.server.parser_process',
            'caliper.server.run',
            'caliper.server.shared',
            'caliper.server.upload',
            #'caliper.benchmarks',
            'caliper.server',
            #'caliper.config',
            #'caliper.utils',
            #'caliper.docs',
            'caliper']

def get_package_data():
    return {'caliper': [],
            'caliper.server': ['build/build.sh', 'build/building_timing.yaml']}

def get_scripts():
    return ['server/../caliper',
            'server/caliper-prerequisite',
            'config/ansible.cfg', 
            'config/cases_config.json', 
            'config/project_config.cfg',
            'config/push_sshkey.yml']

def get_package_dirs():
    #return { 'caliper.server': 'server'}  
    return {'caliper': 'server/..', 'caliper.server': 'server'}  

setup(
        name='caliper',
        version=common.VERSION,
        description='A test suite for automatically running on different\
            devices, and compare the test results',
        package_dir=get_package_dirs(),
        #package_data=get_package_data(),
        packages=get_packages(),
        data_files=get_data_files(),
        scripts=get_scripts(),
        author='James Zhang',
        author_email='zhangxinjia@huawei.com',
        url='http://github.com/hubzhangxj/caliper',
        maintainer="sailing",
        install_requires=[
          'PyYAML>=3.10',
          'poster>=0.8.1']
        )




