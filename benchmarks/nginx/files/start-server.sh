#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

#sh scripts/start-nginx-lb.sh
#sh scripts/start-nginx-proxy.sh
/tmp/nginx/files/scripts/start-nginx-webserver.sh
