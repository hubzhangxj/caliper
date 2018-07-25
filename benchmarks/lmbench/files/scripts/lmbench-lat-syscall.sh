#!/bin/bash

cd lmbench-3.0-a9/bin/lmbench

echo '*********************************'
echo '      lmbench lat_syscall 128K   '
echo '*********************************'
export LMBENCH_SCHED="DEFAULT"

echo '**********2P core0*************'
for THREAD_NUM in 1
do
	for p in null read write stat fstat open
	do
	    numactl -C 0 --localalloc ./lat_syscall -P $THREAD_NUM -N 5 $p
	done
done

echo '**********2P die0*************'
for THREAD_NUM in 16
do
	for p in null read write stat fstat open
	do
	    numactl -C 0-15 --localalloc ./lat_syscall -P $THREAD_NUM -N 5 $p
	done
done

echo '**********2P CPU0*************'
for THREAD_NUM in 32
do
	for p in null read write stat fstat open
	do
		numactl -C 0-31 --localalloc ./lat_syscall -P $THREAD_NUM -N 5 $p
	done
done

echo '**********2P CPU0,1*************'
for THREAD_NUM in 64
do
	for p in null read write stat fstat open
	do
		numactl -C 0-63 --localalloc ./lat_syscall -P $THREAD_NUM -N 5 $p
	done
done
