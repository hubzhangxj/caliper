#!/bin/bash

#LMBENCH_URL=https://nchc.dl.sourceforge.net/project/lmbench/development/lmbench-3.0-a9/lmbench-3.0-a9.tgz
#
#if [ ! -d lmbench-3.0-a9 ]; then
#	if [ ! -f lmbench-3.0-a9.tgz ]; then
#		wget $LMBENCH_URL
#	fi
#	tar xf lmbench-3.0-a9.tgz
#fi
#
if $(which yum > /dev/null 2>&1); then
	yum install -y numactl
fi

if $(which apt > /dev/null 2>&1); then
	apt-get install -y numactl
fi

cd ../ 
sed -i s/-O\ /-O2\ /g src/Makefile

make OS=lmbench
