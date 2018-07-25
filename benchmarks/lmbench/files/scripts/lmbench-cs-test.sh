#!/bin/bash

cd lmbench-3.0-a9/bin/lmbench

echo '*********************************'
echo '      lmbench bw_ctx     128K    '
echo '*********************************'
export LMBENCH_SCHED="DEFAULT"

echo '**********2P core0*************'
for THREAD_NUM in 1
do
	for size in  128K
	do
		for p in 2 4 8 16 32 64
		do
		    numactl -C 0 --localalloc ./lat_ctx -P $THREAD_NUM -N 5 -s $size $p
		done
	done
done


echo '***********2P clu0**************'
for THREAD_NUM in 4
do
	for size in  128K
	do
		for p in 2 4 8 16 32 64
		do
			 numactl -C 0-3 --localalloc ./lat_ctx -P $THREAD_NUM -N 5 -s $size $p
		done
	done
done

echo '**************2P die0**************'
for THREAD_NUM in 16
do
	for size in  128K
	do
		for p in 2 4 8 16 32 64
		do
			numactl -C 0-15 --localalloc ./lat_ctx -P $THREAD_NUM -N 5 -s $size $p
		done
	done
done

echo '**********2P CPU0*************'
for THREAD_NUM in 32
do
	for size in  128K
	do
		for p in 2 4 8 16 32 64
		do
			numactl -C 0-31 --localalloc ./lat_ctx -P $THREAD_NUM -N 5 -s $size $p
		done
	done
done

echo '**********2P CPU0,1*************'
for THREAD_NUM in 64
do
	for size in  128K
	do
		for p in 2 4 8 16 32 64
		do
			numactl -C 0-63 --localalloc ./lat_ctx -P $THREAD_NUM -N 5 -s $size $p
		done
	done
done

