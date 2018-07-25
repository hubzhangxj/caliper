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
			 numactl -C 0-3 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done

echo '**************local die 16core**************'
for THREAD_NUM in 16
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-15 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm   2>&1
		done
	done
done

echo '**********local die 32core*************'
for THREAD_NUM in 32
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-31 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm   2>&1
		done
	done
done

echo '**********local die 64core*************'
for THREAD_NUM in 64
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl -C 0-63 --localalloc ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done

echo '**********cross die 1core*************'
for THREAD_NUM in 1
do
	for size in  32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
		   numactl --membind=1 --physcpubind=0  ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
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
			numactl --membind=1 --physcpubind=0-3 ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done

echo '**************cross die 16core bind1**************'
for THREAD_NUM in 16
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl --membind=1 --physcpubind=0-15 ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done

echo '**************cross die 16core bind2**************'
for THREAD_NUM in 16
do
	for size in 32M
	do
		for bm in rd frd wr fwr bzero rdwr cp fcp bcopy
		do
			numactl --membind=2 --physcpubind=0-15 ./bw_mem -P $THREAD_NUM -N 5 $size $bm  2>&1
		done
	done
done
