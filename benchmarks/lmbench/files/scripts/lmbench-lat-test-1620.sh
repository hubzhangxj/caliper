#!/bin/bash

cd ../bin/lmbench

function lat_local_test_trash() {
        echo '********localdie 1core ***********'
        numactl --membind=0 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 -t 256M 128 2>&1
        echo '********localdie 4core ***********'
        numactl --membind=0 --physcpubind=0-3 ./lat_mem_rd -P 4 -N 5 -t 256M 128 2>&1
        echo '********localdie 16core ***********'
        numactl --membind=0 --physcpubind=0-23 ./lat_mem_rd -P 24  -N 5 -t 256M  128 2>&1
        echo '********localdie 32core ************'
        numactl --physcpubind=0-47 --localalloc ./lat_mem_rd -P 48 -N 5 -t 256M 128 2>&1
        echo '*********localdie 64core ************'
        numactl --physcpubind=0-95 --localalloc ./lat_mem_rd -P 96 -N 5 -t 256M 128 2>&1
}

function lat_local_test_stride() {
        echo '********2P 1core s***********'
        numactl --membind=0 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 256M 128
        echo '********2P 4core s***********'
        numactl --membind=0 --physcpubind=0-3 ./lat_mem_rd -P 4  -N 5 256M 128
        echo '********2P 16core  s***********'
        numactl --membind=0 --physcpubind=0-23 ./lat_mem_rd -P 24  -N 5 256M  128
        echo '********2P CPU0  s************'
        numactl  --physcpubind=0-47 ./lat_mem_rd -P 48  -N 5 256M 128
        echo '********2P CPU12  s************'
        numactl  --physcpubind=0-95 ./lat_mem_rd -P 96  -N 5 256M 128
}

function lat_cross_die_trash() {
        echo '********crossdie 1core ***********'
        numactl --membind=1 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 -t 256M 128 2>&1
        echo '********crossdie 4core ***********'
        numactl --membind=1 --physcpubind=0-3 ./lat_mem_rd -P 4 -N 5 -t 256M 128 2>&1
        echo '********crossdie 16core ***********'
        numactl --membind=1 --physcpubind=0-23 ./lat_mem_rd -P 24  -N 5 -t 256M 128 2>&1
}

function lat_cross_die_stride() {
        echo '********2P  TA->TC 1core s***********'
        numactl --membind=1 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 256M 128
        echo '********2P  TA->TC 4core s***********'
        numactl --membind=1 --physcpubind=0-3 ./lat_mem_rd -P 4  -N 5 256M 128
        echo '********2P  TA->TC 16core  s***********'
        numactl --membind=1 --physcpubind=0-23 ./lat_mem_rd -P 24  -N 5 256M  128
}

function lat_cross_socket_trash() {
        //po->P1
        echo '********crosssocket  1core ***********'
        numactl --membind=2 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 -t 256M 128 2>&1
        echo '********crosssocket  4core ***********'
        numactl --membind=2 --physcpubind=0-3 ./lat_mem_rd -P 4 -N 5 -t 256M 128 2>&1
        echo '********crosssocket  16core ***********'
        numactl --membind=2 --physcpubind=0-23 ./lat_mem_rd -P 24 -N 5 -t 256M 128 2>&1
}

function lat_cross_socket_stride() {
        echo '********2P  P0TA->P1TA  1core s***********'
        numactl --membind=2 --physcpubind=0 ./lat_mem_rd -P 1 -N 5 256M 128
        echo '********2P  P0TA->P1TA  4core s***********'
        numactl --membind=2 --physcpubind=0-3 ./lat_mem_rd -P 4 -N 5 256M 128
        echo '********2P  P0TA->P1TA  16core  s***********'
        numactl --membind=2 --physcpubind=0-23 ./lat_mem_rd -P 24 -N 5 256M  128
}

function lat_cross_socket_die_trash() {
        echo '********P0TB->P1TB  1core t***********'
        numactl --membind=3 --physcpubind=24 ./lat_mem_rd -P 1 -N 5  -t 256M 128
        echo '********P0TB->P1TB    4core t***********'
        numactl --membind=3 --physcpubind=24-27 ./lat_mem_rd -P 4 -N 5 -t 256M 128
        echo '********P0TB->P1TB  ->TC 16core  t***********'
        numactl --membind=3 --physcpubind=24-47 ./lat_mem_rd -P 24 -N 5 -t 256M  128
}

function lat_cross_socket_die_stride() {
        echo '********2P  P0TB->P1TB  1core s***********'
        numactl --membind=3 --physcpubind=24 ./lat_mem_rd -P 1 -N 5 256M 128
        echo '********2P  P0TB->P1TB  4core s***********'
        numactl --membind=3 --physcpubind=24-27 ./lat_mem_rd -P 4 -N 5 256M 128
        echo '********2P  P0TB->P1TB 16core  s***********'
        numactl --membind=3 --physcpubind=24-47 ./lat_mem_rd -P 24 -N 5 256M 128
}

lat_local_test_trash
lat_cross_die_trash
lat_cross_socket_trash












