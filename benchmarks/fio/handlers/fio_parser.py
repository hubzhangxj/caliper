#!/usr/bin/env python

import re
import pdb
import string
import json
from caliper.server.parser_process import parser_log

def bw_parser(content, outfp):
    score = 0
    SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)B')
    pat_search = SEARCH_PAT.search(content)
    SEARCH_PAT_MB = re.compile(r'bw\s*=\s*(\d+\.*\d*)MB')
    pat_search_MB = SEARCH_PAT_MB.search(content)

    if pat_search:
        last_search = str(pat_search.group(1))
        last_search = string.atof(last_search) / 1024.0
        score = last_search
    elif pat_search_MB:
        last_search = str(pat_search_MB.group(1))
        last_search = string.atof(last_search) * 1024
        score = last_search
    else:
        SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)KB')
        last_search = SEARCH_PAT.search(content)
        outfp.write("bw:" + str(last_search.group(1)) + "KB/s\n")
        score = last_search.group(1)
    return score


def iops_parser(content, outfp):
    score = 0
    SEARCH_PAT = re.compile(r'iops\s*=\s*(\d+)')
    pat_search = SEARCH_PAT.search(content)
    outfp.write("bw:"+pat_search.group(1)+"\n")
    score = pat_search.group(1)
    return score

def fio(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search('\[test:([\s\S]+)\.\.\.', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)
            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        tables = []
        tableContent = {}
        centerTopGroup = re.search("(fio\-[\s\S]+\s20\d\d\n)", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]

        tableGroup = re.search("\s20\d\d\n([\s\S]+)\[status\]", case)
        if tableGroup is not None:
            tableGroupContent = tableGroup.groups()[0].strip()
            tableGroupContent_temp = re.sub("(clat percentiles[\s\S]+\]\n)", "", tableGroupContent)
            table = parser_log.parseTable(tableGroupContent_temp, ":{1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "fio_output.log"
    outfile = "fio_json.txt"
    outfp = open(outfile, "a+")
    fio(infile, outfp)
    outfp.close()
