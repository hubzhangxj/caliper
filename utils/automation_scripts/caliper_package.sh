#!/bin/bash
## How to build caliper_[var].install

#check user
user=`whoami`
if [ "$user" = 'root' ]; then
    echo "Please run this program as a normal user!"
    exit 0
fi

cd `dirname $0` 
 
tar cvzf caliper.tar.gz ../../../caliper 

var=`cat ../../common.py | grep -owP "VERSION=\K\S+" | sed 's/\"//g'`

cat install.sh caliper.tar.gz > $HOME/caliper-$var.install

md5sum $HOME/caliper-$var.install > $HOME/caliper-$var.install.md5

chmod 775 $HOME/caliper-$var.install

rm -rf caliper.tar.gz
