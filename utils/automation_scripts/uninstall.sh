#!/bin/bash

## write the start time of the uninstallation to the log file
uninstall_date()
{
    echo "[uninstall_date]" >> $log 
    echo date=$(date +%Y-%m-%d_%H:%M:%S) >> $log 
}

## uninstall caliper 
uninstall_caliper()
{
    sudo pip uninstall caliper -y > /dev/null 2>&1

    sudo rm -f /usr/local/bin/caliper
}

## uninstall pip new packages
uninstall_pip()
{
    tmp_log="/tmp/caliper_tmp.log"
    packs=`cat $HOME/caliper_output/install*.log | grep "pip install success" | uniq | sed 's/\ .*$//'`
    for pack in $packs
    do
        for((num=1;num<=3;num++))
        do
            sudo LC_ALL=C pip uninstall $pack -y >/dev/null 2>&1
            if [ $? -eq 0 ]
            then
                echo "$pack pip uninstall success" >> $log
                break
            fi
	    if [ $num -eq 3 ]; then
	        echo "$pack pip uninstall failed" >> $log
	    fi
        done
    done
}

## uninstall dpk new packages
uninstall_pkg()
{
    tmp_log="/tmp/caliper_tmp.log"

    system_os=`cat /etc/os-release | grep -owP 'ID=\K\S+' | sed 's/"//g'`

    case $system_os in
    ubuntu)
        order="apt-get"
	;;
    centos|rhel)
        order="yum"
	;;
    sles)
        order="zypper"
	;;  
    esac

    if [ $system_os = "ubuntu" ]
    then
        packs=`cat $HOME/caliper_output/install*.log | grep "pkg install success" | uniq | sed 's/\ .*$//'`
        for pack in $packs
        do
            for((num=1;num<=3;num++))
            do
                sudo $order autoremove $pack -y > $tmp_log 2>&1
                if [ $? -eq 0 ]
                then
                    echo "$pack pkg uninstall success" >> $log 2>&1
		    break
                fi
	        if [ $num -eq 3 ]; then
                    echo "$pack pkg uninstall failed" >> $log 2>&1
	        fi
            done
        done
    else
        packs=`cat $HOME/caliper_output/install*.log | grep "pkg install success" | uniq | sed 's/\ .*$//'`
        for pack in $packs
        do
            for((num=1;num<=3;num++))
            do
                if [ "x$order" = "xzypper" ]
                then
                    sudo $order remove -y $pack > $tmp_log 2>&1
                else
                    sudo $order autoremove $pack -y > $tmp_log 2>&1
                fi

                if [ $? -eq 0 ]
                then
                    echo "$pack pkg uninstall success" >> $log
                    break
                fi
	        if [ $num -eq 3 ]; then
                    echo "$pack pkg uninstall failed" >> $log 2>&1
	        fi
            done
        done
    fi
}
 
## main
main()
{
## 1. check user

#    user=`whoami`
#    if [ "$user" = "root" ]
#    then
#        show_message 0 "   Please run this program as normal user." 7 48
#    fi

## 1. check if caliper is installed
    which caliper
    if [ $? -ne 0 ]; then
        whiptail --title "Error" --msgbox "             Could not find caliper." 7 55
#	exit 1
    fi

## 2. create log file

    log="$HOME/caliper_output/uninstall_$(date +%Y-%m-%d_%H-%M-%S).log"
    if [ ! -f $log ]
    then 
        touch $log
    fi
    sudo chown $user:$user $log
    
## 3. read the installation log file

#    cat /opt/Caliper/install*.log | grep "caliper install success"
#    if [ $? -ne 0 ]
#    then
#        show_message 0 "    checking install log fail then exit ..." 7 50 
#    fi 
 
## 4. write uninstall date

    {
    	uninstall_date
    } | whiptail --title "Uninstall" --gauge "prepare log file" 7 55 10

## 5. uninstall caliper

    echo "[uninstall_caliper]" >> $log
    {
    	uninstall_caliper
	echo " caliper uninstall success" >> $log
    } | whiptail --title "Uninstall" --gauge "Uninstall caliper" 7 55 20

## 6. uninstall pip packages
    
    echo "[uninstall_pip]" >> $log
    {
    	uninstall_pip 
    } | whiptail --title "Uninstall" --gauge "Uninstall pip packages" 7 55 40

## 7. uninstall dpkg/rpm pacakges

    echo "[uninstall_pkg]" >> $log
    {
    	uninstall_pkg
    } | whiptail --title "Uninstall" --gauge "Uninstall dpkg/rpm packages" 7 55 70

## 8. remove output 

    whiptail --yesno "Please choose remove ~/caliper_output" --defaultno 7 58
    choose_status=$?
    if [ $choose_status -eq 0 ]
    then
        rm -rf ~/caliper_output
    fi

## 9. finish
   whiptail --title "uninstall caliper" --msgbox "             uninstall caliper finished." 7 58 
   exit 0
}

main
