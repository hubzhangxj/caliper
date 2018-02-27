*****************************************
** How to make caliper install package **
*****************************************

1 Get caliper source code by git clone

  $ git clone https://github.com/TSestuary/caliper

2 (optional) Modify software version by modify
  caliper/common.py. The keyword is VERSION

  VERSION="0.3.8"  

3 Run the script caliper_package.sh to build the 
  install package

  $ cd caliper/utils/automation_scripts
  $ ./caliper_package.sh

  The install package will be $HOME/caliper-$VERSION.install,
  and the md5 file will generated.

