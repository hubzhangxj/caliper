import re
import string
import pdb
import sys
import json
import yaml
from caliper.server.parser_process import parser_log

local_mem_lat_dic = {'lat_0_5KB': 'lb_lat_00_0.5KB',
                     'lat_1KB': 'lb_lat_01_01KB',
                     'lat_2KB': 'lb_lat_02_2KB',
                     'lat_3KB': 'lb_lat_03_3KB',
                     'lat_4KB': 'lb_lat_04_4KB',
                     'lat_6KB': 'lb_lat_05_6KB',
                     'lat_8KB': 'lb_lat_06_8KB',
                     'lat_12KB': 'lb_lat_07_12KB',
                     'lat_16KB': 'lb_lat_08_16KB',
                     'lat_24KB': 'lb_lat_09_24KB',
                     'lat_32KB': 'lb_lat_10_32KB',
                     'lat_48KB': 'lb_lat_11_48KB',
                     'lat_64KB': 'lb_lat_12_64KB',
                     'lat_96KB': 'lb_lat_13_96KB',
                     'lat_128KB': 'lb_lat_14_128KB',
                     'lat_192KB': 'lb_lat_15_192KB',
                     'lat_256KB': 'lb_lat_16_256KB',
                     'lat_384KB': 'lb_lat_17_384KB',
                     'lat_512KB': 'lb_lat_18_512KB',
                     'lat_768KB': 'lb_lat_19_768KB',
                     'lat_1MB': 'lb_lat_20_1MB',
                     'lat_1_5MB': 'lb_lat_21_1.5MB',
                     'lat_2MB': 'lb_lat_22_2MB',
                     'lat_3MB': 'lb_lat_23_3MB',
                     'lat_4MB': 'lb_lat_24_4MB',
                     'lat_6MB': 'lb_lat_25_6MB',
                     'lat_8MB': 'lb_lat_26_8MB',
                     'lat_12MB': 'lb_lat_27_12MB',
                     'lat_16MB': 'lb_lat_28_16MB',
                     'lat_24MB': 'lb_lat_29_24MB',
                     'lat_32MB': 'lb_lat_30_32MB',
                     'lat_48MB': 'lb_lat_31_48MB',
                     'lat_64MB': 'lb_lat_32_64MB',
                     'lat_96MB': 'lb_lat_33_96MB',
                     'lat_128MB': 'lb_lat_34_128MB',
                     'lat_192MB': 'lb_lat_35_192MB',
                     'lat_256MB': 'lb_lat_36_256MB'}

def lmbench_bw(content, outfp):
    dic = {}
    dic['bandwidth'] = {}
    dic['bandwidth']['local die 1core'] = {}
    dic['bandwidth']['local die 4core'] = {}
    dic['bandwidth']['local die 12core'] = {}
    dic['bandwidth']['local die 24core'] = {}
    dic['bandwidth']['local die 48core'] = {}
    dic['bandwidth']['2P cross cpu 1core'] = {}
    dic['bandwidth']['2P cross cpu 24 core'] = {}
    try:
        for key in dic['bandwidth'].keys():
            contents = content
            if re.search(key, content):
                content = re.search("\**%s\**([\s\S]+)" % key, content)
                value_list = re.findall("(\d+\.\d+\s\d+\.\d+)\n", content.group(0), re.DOTALL)
                dic['bandwidth'][key]['rd'] = value_list[0].split()[-1]
                outfp.write("bandwidth %s rd: "%key + str(dic['bandwidth'][key]['rd']) + '\n')
                dic['bandwidth'][key]['frd'] = value_list[1].split()[-1]
                outfp.write("bandwidth %s frd: "%key + str(dic['bandwidth'][key]['frd']) + '\n')
                dic['bandwidth'][key]['wr'] = value_list[2].split()[-1]
                outfp.write("bandwidth %s wr: "%key + str(dic['bandwidth'][key]['wr']) + '\n')
                dic['bandwidth'][key]['fwr'] = value_list[3].split()[-1]
                outfp.write("bandwidth %s fwr: "%key + str(dic['bandwidth'][key]['fwr']) + '\n')
                dic['bandwidth'][key]['bzero'] = value_list[4].split()[-1]
                outfp.write("bandwidth %s bzero: "%key + str(dic['bandwidth'][key]['bzero']) + '\n')
                dic['bandwidth'][key]['rdwr'] = value_list[5].split()[-1]
                outfp.write("bandwidth %s rdwr: " %key + str(dic['bandwidth'][key]['rdwr']) + '\n')
                dic['bandwidth'][key]['cp'] = value_list[6].split()[-1]
                outfp.write("bandwidth %s cp: "% key + str(dic['bandwidth'][key]['cp']) + '\n')
                dic['bandwidth'][key]['fcp'] = value_list[7].split()[-1]
                outfp.write("bandwidth %s fcp: " %key+ str(dic['bandwidth'][key]['fcp']) + '\n')
                dic['bandwidth'][key]['bcopy'] = value_list[8].split()[-1]
                outfp.write("bandwidth %s bcopy: " %key+ str(dic['bandwidth'][key]['bcopy']) + '\n')
            content = contents
    except:
        dic['bandwidth'] = {}
    return dic

def lmbench_lat(content, outfp):
    dic = {}
    dic['lat'] = {}
    dic['lat']['localdie 1core '] = {}
    dic['lat']['localdie 12core '] = {}
    dic['lat']['localdie 24core '] = {}
    dic['lat']['localdie 48core '] = {}
    dic['lat']['cross socket  1core t'] = {}
    dic['lat']['cross socket  12core  '] = {}
    dic['lat']['cross socket  24core  '] = {}
    for key in dic['lat'].keys():
        contents = content
        if re.search(key, content):
            content = re.search("\**%s\**([\s\S]+)" % key, content)
            value_list = re.findall("(\d+\.\d+\s\d+\.\d+)\n", content.group(0), re.DOTALL)
            dic['lat'][key][local_mem_lat_dic['lat_0_5KB']] = value_list[0].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_1KB']] = value_list[1].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_2KB']] = value_list[2].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_3KB']] = value_list[3].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_4KB']] = value_list[4].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_6KB']] = value_list[5].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_8KB']] = value_list[6].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_12KB']] = value_list[7].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_16KB']] = value_list[8].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_24KB']] = value_list[9].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_32KB']] = value_list[10].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_48KB']] = value_list[11].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_64KB']] = value_list[12].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_96KB']] = value_list[13].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_128KB']] = value_list[14].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_192KB']] = value_list[15].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_256KB']] = value_list[16].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_384KB']] = value_list[17].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_512KB']] = value_list[18].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_768KB']] = value_list[19].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_1MB']] = value_list[20].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_1_5MB']] = value_list[21].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_2MB']] = value_list[22].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_3MB']] = value_list[23].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_4MB']] = value_list[24].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_6MB']] = value_list[25].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_8MB']] = value_list[26].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_12MB']] = value_list[27].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_16MB']] = value_list[27].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_24MB']] = value_list[29].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_32MB']] = value_list[30].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_48MB']] = value_list[31].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_64MB']] = value_list[32].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_96MB']] = value_list[33].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_128MB']] = value_list[34].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_192MB']] = value_list[35].split()[-1]
            dic['lat'][key][local_mem_lat_dic['lat_256MB']] = value_list[36].split()[-1]
        content = contents
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic

def lmbench(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search("\[test:([\s\S]+?)\]", case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)

        tables = []
        tableContent = {}
        tableContent[parser_log.CENTER_TOP] = ''
        tableGroup = re.search("log:[\s\S]*?\n([\s\S]+)\[status\]", case)
        if tableGroup is not None:
            tableGroupContent = tableGroup.groups()[0].strip()
            table = parser_log.parseTable(tableGroupContent, "\\s{1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infp = open("lmbench_lat.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    a = lmbench_lat(content, outfp)
    outfp.close()
    infp.close()
    infile = "lmbench_lat.log"
    outfile = "lmbench.json"
    outfp = open(outfile, "a+")
    lmbench(infile, outfp)
    outfp.close()

