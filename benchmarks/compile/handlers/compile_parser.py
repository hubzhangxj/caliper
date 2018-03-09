#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time_parser
import re
import json
from caliper.server.parser_process import parser_log

def compile_parser(content, outfp):
    return time_parser.time_parser(content, outfp)

def compile(filePath, outfp):
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
        tableGroup = re.search("(real	[\s\S]+)\[status\]", case)
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
    infile = "compile_output.log"
    outfile = "compile_json.txt"
    outfp = open(outfile, "a+")
    compile(infile, outfp)
    outfp.close()
