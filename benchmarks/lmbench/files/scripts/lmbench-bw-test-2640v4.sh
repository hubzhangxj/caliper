#!/bin/bash

cd ../bin/lmbench

echo '*********************************'
echo '      lmbench bw_mem     32M       '
echo '*********************************'
export LMBENCH_SCHED="DEFAULT"

echo '**********local die 1core*************'
for THREAD_NUM in 1
do
	for size in  32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
		    numactl -C 0 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done

echo '**************local die 10core**************'
for THREAD_NUM in 10
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-9 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1
		done
	done
done

echo '**********local die 20core*************'
for THREAD_NUM in 20
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl --cpunodebind=0 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1
		done
	done
done

echo '**********local die 48core*************'
for THREAD_NUM in 40
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-39 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1
		done
	done
done

echo '**********2P cross cpu 1core *************'
for THREAD_NUM in 1
do
	for size in  32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
		   numactl --membind=1 --physcpubind=0  ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1
		done
	done
done

echo '**************2P cross cpu 20 core**************'
for THREAD_NUM in 20
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl --membind=1 --cpunodebind=0 ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1
		done
	done
done
