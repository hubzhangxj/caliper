#!/bin/bash
## How to build caliper_[var].install

#check user
user=`whoami`
if [ "$user" = 'root' ]; then
    echo "Please run this program as a normal user!"
    exit 0
fi

cd `dirname $0` 
 
tar cvzf $HOME/caliper.tar.gz ../../../caliper --exclude=.git

var=`cat ../../common.py | grep -owP "VERSION=\K\S+" | sed 's/\"//g'`

cat install.sh $HOME/caliper.tar.gz > $HOME/caliper-$var.install

md5sum $HOME/caliper-$var.install > $HOME/caliper-$var.install.md5

chmod 775 $HOME/caliper-$var.install

rm -f caliper.tar.gz

rm -f $HOME/caliper-v$var.zip
cd $HOME && zip caliper-v$var.zip caliper-$var.install caliper-$var.install.md5
