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

echo '***********local die 4core**************'
for THREAD_NUM in 4
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			 numactl -C 0-3 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1 
		done
	done
done

echo '**************local die 12core**************'
for THREAD_NUM in 12
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-11 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1 
		done
	done
done

echo '**********local die 24core*************'
for THREAD_NUM in 24
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
for THREAD_NUM in 48
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-47 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1 
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

echo '**************2P cross cpu 24 core**************'
for THREAD_NUM in 24
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl --membind=1 --cpunodebind=0 ./bw_mem -P $THREAD_NUM -N 5 $size $bm 2>&1 
		done
	done
done
