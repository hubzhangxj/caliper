#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pdb


import os
import time
import json
import platform
import subprocess
from progressbar import *

def install_method(distro):
    return {
            'Ubuntu': 'apt-get -y install ',
            'CentOS': 'yum -y install',
            'CentOS Linux': 'yum -y install',
            'Redhat': 'yum -y install',
            'slse': 'zyyper',
    }.get(distro,'error')

project_config_path = os.path.join(os.getcwd(),'depend.json') 

if __name__ == '__main__':
    f = open( project_config_path,'r')
    project_depend = f.read()
    f.close()
    #print json.loads(project_depend)
    #print project_config_path
    #platform.linux_distribution()
    #('Ubuntu', '18.04', 'bionic')
    distro = platform.linux_distribution()[0].split()[0]
    install_cmd=install_method(distro)
    project_depend_install = json.loads(project_depend)
    #print listunit['centos_dpk_package'][0].keys()
    #listunit['centos_dpk_package'][0].values()
    #if distro == 'ubuntu':
    distro_listlen = len(project_depend_install[distro])
    install_listlen = len(project_depend_install[distro]) + len(project_depend_install['pip'])
    total_len = install_listlen + 1
    #print "install len %d " % total_len
    widgets = ['Progress: ',Percentage(), ' ', Bar('#'),' ', Timer(),' ', ETA(), ' ', FileTransferSpeed()]
    #pbar = ProgressBar(widgets=widgets, maxval=10*total).start()
    pbar = ProgressBar(widgets=widgets, maxval=10*total_len).start()

    try:
       #print   project_depend_install[distro][0]
       for i in range( total_len):
           # print "Num i:%d is install_listlen:%d " % (i, install_listlen) 
           if i < distro_listlen :
               install_pkg = (''.join(project_depend_install[distro][i].keys()))
               install_judge = (''.join(project_depend_install[distro][i].values()))
           #print "=======Num %s install %s============" %(i, type(int(install_judge)))
           elif i < install_listlen :
               j = i -distro_listlen
               install_cmd='pip install'
               install_pkg = (''.join(project_depend_install['pip'][j].keys()))
               install_judge = (''.join(project_depend_install['pip'][j].values()))
           else:
              #pdb.set_trace()
              abs_path = os.path.abspath('..')
              base_path = os.path.split(abs_path)[0]
              install_cmd = 'python'
              install_pkg = 'setup.py install'
              os.chdir(base_path)
           #print "=======Num %d install %s============" %(i, install_pkg)
               
               #retcode = subprocess.call("%s %s" % ( install_cmd, install_pkg), shell=True) 
           subprocess.call("%s %s" % ( install_cmd, install_pkg), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

           pbar.update(10 * i + 10)
    
    except Exception as ie:
        print 'it\'s not exit %s ' % distro
        print ie

