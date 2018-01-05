import re
import string
import pdb
import sys
import json
from caliper.server.parser_process import parser_log

def get_average_value(content, outfp, flag_str):
    score = -1
    if re.search(flag_str, content):
        score = 0
        sum_value = 0
        i = 0
        for line in re.findall("(\d+\s+\d+\.\d+\s*)\n", content, re.DOTALL):
            tmp_data = line.split()[-1]
            try:
                tmp_value = string.atof(tmp_data)
            except Exception, e:
                print e
                continue
            else:
                sum_value = sum_value + tmp_value
                i = i + 1
        try:
            score = sum_value / i
        except Exception, e:
            print e
            score = 0
        return score


def cachebench_read_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)_r")
    outfp.write("read bandwidth: " + str(score) + '\n')
    return score


def cachebench_write_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)_w")
    outfp.write("write bandwidth: " + str(score) + '\n')
    return score


def cachebench_modify_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)_M")
    outfp.write("read/mdify/write bandwidth: " + str(score) + '\n')
    return score

def cachebench(filePath, outfp):
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
    infile = "cachebench_output.log"
    outfile = "cachebench_json.txt"
    outfp = open(outfile, "a+")
    cachebench(infile, outfp)
    outfp.close()
