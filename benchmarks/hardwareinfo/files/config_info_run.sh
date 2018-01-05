#!/bin/bash
# !!! this script must run as root !!!

#the output file
output_file=/tmp/hardwareinfo.json

#the hw-functions must save in this base_dir
base_dir=./

hostfile=$HOME/caliper_output/configuration/config/hosts

datestr=`date +%s`
dmidecode_file=/tmp/dmi_$datestr
lshw_file=/tmp/lshw_$datestr
lsblk_file=/tmp/lsblk_$datestr
ansible_file=/tmp/ansibleout_$datestr


. $base_dir/hw-functions

# generate files by dmidecode, lshw, lsblk and ansible
# these files will be used for later analyse.
generate_files() {
    dmidecode -q > $dmidecode_file
    lshw -json > $lshw_file
    lsblk -O -J | sed 's/log-sec/logsec/g' > $lsblk_file

    ansible localhost -m setup > $ansible_file.tmp
    echo "{" > $ansible_file
    sed '1d' $ansible_file.tmp >> $ansible_file
    rm $ansible_file.tmp
}

init_outputfile() {
    echo "{" > $1
}

close_outputfile() {
    echo "}" >> $1
}

#main 
generate_files

init_outputfile $output_file

parse_baseconfig $ansible_file $output_file
parse_system $ansible_file $output_file
parse_baseboard $dmidecode_file $output_file
parse_cpu $dmidecode_file $output_file
parse_memory $dmidecode_file $output_file
parse_cache $dmidecode_file $output_file
parse_storage $lsblk_file $output_file
parse_network $ansible_file $output_file

close_outputfile $output_file

