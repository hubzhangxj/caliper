#!/usr/bin/env python
import re
import string
import operator
import json
from caliper.server.parser_process import parser_log

#finished in 2 sec, 697 millisec and 187 microsec, 9268 req/s, 7693 kbyte/s
#requests: 25000 total, 25000 started, 25000 done, 25000 succeeded, 0 failed, 0 errored
# TOTALS:  10000 connect, 10000 requests, 0 success, 10000 fail, 0 (0) real concurrency

def nginx_parser(content, outfp):
    dic = {}
    dic['wrps'] = 0
    dic['max_cpu_load'] = 0

    cpu_load_dic = {}
    i = 0
    flag = 0

    for contents in re.findall("TOTALS:  (.*?)\s+concurrency", content, re.DOTALL):
        fail_count = re.search(r'.*?(\d+)\s+fail.*?', contents)

        counts = fail_count.group(1)
        if counts == "0":
            for wrps in re.findall("\s+.*?(\d+)\s+requests.*?", contents):
                wrps_final = string.atof(wrps.strip())
                outfp.write("wrps is %s \n" % wrps_final)
                wrps_final = float(wrps_final / 10000.0)
                dic['wrps'] = dic['wrps'] + wrps_final
                flag = 1

    # for dstat_data in re.findall("\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\|.*?" , content):
    #     outfp.write("dstat data is %s \n" % dstat_data)
    #     key = "cpu_load" + str(i)
    #     cpu_load_dic[key] = string.atoi(dstat_data.strip())
    #     i = i + 1
    #     flag = 2
    # if flag == 2:
    #     max_cpu_load = min(cpu_load_dic.iteritems(), key=operator.itemgetter(1))[1]
    #     dic['max_cpu_load'] = 100 - max_cpu_load
    # if dic['wrps'] == 0 or dic['max_cpu_load'] == 0:
    #     dic = {}
    # dic['wrps'] = 1
    # dic['max_cpu_load'] = 1

    return dic

def nginx(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search('\[test:([\s\S]+)nginx_run', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)
            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        tables = []
        tableContent = {}
        centerTopGroup = re.search("\.*([\s\S]+10000 requests launched)", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        print tableContent[parser_log.CENTER_TOP]
        # centerTopGroup = re.search("\*\*\n([\s\S]+)10000 requests launched", case)
        # tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("10000 requests launched\.*([\s\S]+time)", case)
        if tableGroup is not None:
            tableGroupContent_temp = tableGroup.groups()[0].strip()
            # tableGroupContent = re.sub(':([\s]+)Mflops:', ' Mflops:', tableGroupContent_temp)
            table = parser_log.parseTable(tableGroupContent_temp, ":{1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infp = open("nginx_output.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    # for data in content:
    #     print data
    a = nginx_parser(content, outfp)
        #print a

    outfp.close()
    infp.close()
    # infile = "nginx_output.log"
    # outfile = "nginx.json"
    # outfp = open(outfile, "a+")
    # nginx(infile, outfp)
    # outfp.close()
