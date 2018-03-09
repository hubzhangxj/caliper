#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

/tmp/nginx/files/scripts/build-libev.sh
/tmp/nginx/files/scripts/build-httpress.sh
