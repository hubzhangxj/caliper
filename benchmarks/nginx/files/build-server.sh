#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

/tmp/nginx/files/scripts/build-nginx.sh
#sh scripts/make-ca.sh
