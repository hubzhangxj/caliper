#!/bin/bash

cd ../bin/lmbench

function lat_local_test_trash() {
	echo '********localdie 1core ***********'
	numactl --membind=0 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 -t 256M 128 2>&1
	echo '********localdie 10core ***********'
	numactl --membind=0 --physcpubind=0-9 ./lat_mem_rd -P 10  -N 5 -t 256M  128 2>&1
	echo '********localdie 20core ************'
	numactl --membind=0 --cpunodebind=0 ./lat_mem_rd -P 20 -N 5 -t 256M 128 2>&1
	echo '********localdie 40core ************'
	numactl --localalloc --cpunodebind=0,1 ./lat_mem_rd -P 40 -N 5 -t 256M 128 2>&1
}

function lat_cross_socket_trash() {
	echo '********cross socket  1core t***********'
	numactl --membind=1 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 -t 256M 128 2>&1
	echo '********cross socket  10core  ***********'
	numactl --membind=1 --physcpubind=0-9 ./lat_mem_rd -P 10 -N 5 -t 256M  128 2>&1
	echo '********cross socket  20core  ***********'
	numactl --membind=1 --cpunodebind=0 ./lat_mem_rd -P 20 -N 5 -t 256M  128 2>&1
}

lat_local_test_trash
lat_cross_socket_trash
