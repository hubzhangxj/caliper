#!/usr/bin/python

import re
import string
import json
from caliper.server.run import parser_log

def coremark_parser(content, outfp):
    score = -1
    m = re.search("Iterations/Sec(.*?)\n", content)
    if m:
        score = 0
        lastline = content.splitlines()[-1]
        outfp.write(lastline + '\n')
        score_tmp = lastline.split(":")[-1].strip().split("/")[0]
        try:
            score_latter = string.atof(score_tmp)
        except Exception, e:
            print e
        else:
            score = score_latter
        return score

def coremark(filePath, outfp):
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
        centerTopGroup = re.search("log:[\s\S]*?\n([\s\S]+for coremark\.)?\n", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("for coremark\.\n([\s\S]+)\nMemory location", case)
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
    infile = "coremark_output.log"
    outfile = "coremark_json.txt"
    outfp = open(outfile, "a+")
    coremark(infile, outfp)
    outfp.close()
