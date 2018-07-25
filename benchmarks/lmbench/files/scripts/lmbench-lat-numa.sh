#!/bin/sh

#set -x

function lat_numa_trash_1core() {
	local bindcore=$1
	local bindmem=$2

	numactl --physcpubind=$bindcore --membind=$bindmem ./lat_mem_rd -P 1 -N 5 -t 256M 128
}

function lat_numa_trash_1die() {
	local binddie=$1
	local bindmem=$2

	numactl --cpubind=$binddie --membind=$bindmem ./lat_mem_rd -P 16 -N 5 -t 256M 128
}

cd lmbench-3.0-a9/bin/lmbench

for ((i=0;i<64;i=i+16)); do
	for ((j=0;j<4;j++)); do
		lat_numa_trash_1core $i $j
	done
done

for ((i=0;i<4;i++)); do
	for ((j=0;j<4;j++)); do
		lat_numa_trash_1die $i $j
	done
done
