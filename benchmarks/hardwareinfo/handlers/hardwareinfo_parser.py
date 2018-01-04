#!/usr/bin/python
import yaml
import os
import shutil
import caliper.server.shared.caliper_path as caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder

def hardware_info_parser(content,outfp):
    try:
        if not os.path.exists(Folder.json_dir):
            os.mkdir(Folder.json_dir)
        shutil.copy('/tmp/config_output.json', os.path.join(Folder.json_dir, 'config_output.json'))
    except Exception,e:
        pass
    dic = {}
    dic_yaml = {}
    dic_yaml['Configuration'] = {}
    dic_yaml['name'] = {}
    with open(Folder.config_output_json, 'r') as fp:
        dic = yaml.load(fp.read())
    # outfp.write(dic)
    dic_yaml['Configuration'] = dic
    dic_yaml['name'] = dic['hostName']
    yaml_name = caliper_path.platForm_name + ".yaml"
    yaml_path = os.path.join(Folder.yaml_dir, yaml_name)
    with open(yaml_path,'w') as outfp:
        outfp.write(yaml.dump(dic_yaml, default_flow_style = False))
    yaml_name_hw = caliper_path.platForm_name + "_hw_info.yaml"
    yaml_path_hw = os.path.join(Folder.yaml_dir, yaml_name_hw)
    with open(yaml_path_hw,'w') as outfp:
        outfp.write(yaml.dump(dic,default_flow_style = False))
    return dic

def hardwareinfo(content,outfp):
    pass


if __name__ == "__main__":
    infp = open("hardware_info_output.log", "r")
    content = infp.read()
    outfp = open("hardware_info_parser.log", "a+")
    hardware_info_parser(content, outfp)
    outfp.close()
    infp.close()
