#!/usr/bin/env python

import re
import pdb
import json
from caliper.server.run import parser_log

def common_parser(content, outfp, unit):
    score = -1
    lines = content.splitlines()

    test = re.findall('(.*)from', content)
    if test:
        test_case = test[0].strip()
        flag = 0
        for i in range(0, len(lines)):
            if flag == 1:
                break
            if re.search(unit, lines[i]):
                for j in range(i+1, len(lines)):
                    if ((len(lines[j].split()) >= 5) and
                            re.match('\d+', lines[j].split()[0])):
                        score = lines[j].split()[-1]
                        flag = 1
                        break
    	outfp.write(test_case + ' ' + str(score) + '\n')
    else:
        score = 0
    return score


def throughput_parser(content, outfp):
    return common_parser(content, outfp, 'Throughput')


def frequent_parser(content, outfp):
    return common_parser(content, outfp, 'Rate')

def netperf(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search('\[test:([\s\S]+?)\]', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)
            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        tables = []
        tableContent = {}
        centerTopGroup = re.search("(MIGRATED[\S\ ]+)\n", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("MIGRATED[\S\ ]+\n?([\s\S]+)\[status\]", case)
        if tableGroup is not None:
            tableGroupContent = tableGroup.groups()[0].strip()
            tableGroupContent_temp1 = re.sub('per sec', 'per/sec', tableGroupContent)
            table = parser_log.parseTable(tableGroupContent_temp1, "\ {1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "netperf_output.log"
    outfile = "netperf_json.txt"
    outfp = open(outfile, "a+")
    netperf(infile, outfp)
    outfp.close()
