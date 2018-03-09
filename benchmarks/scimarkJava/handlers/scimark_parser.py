#!/usr/bin/python

import re
import string
import json
from caliper.server.parser_process import parser_log

def scimark_parser(content, outfp):
    score = -1
    m = re.search("Composite Score(.*?)\n", content)
    if m:
        score = 0
        line = m.group()
        outfp.write(line)
        score_tmp = line.strip().split(":")[-1].strip()
        try:
            score_latter = string.atof(score_tmp)
        except Exception, e:
            print e
        else:
            score = score_latter
        return score

def scimarkjava(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search('\[test:([\s\S]+)\;', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)
            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        tables = []
        tableContent = {}
        centerTopGroup = re.search("\;\n([\s\S]+)a\n", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("(Composite[\s\S]+)\[", case)
        if tableGroup is not None:
            tableGroupContent = tableGroup.groups()[0].strip()
            table = parser_log.parseTable(tableGroupContent, ":{1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "scimarkJava_output.log"
    outfile = "scimarkjava_json.txt"
    outfp = open(outfile, "a+")
    scimarkjava(infile, outfp)
    outfp.close()
