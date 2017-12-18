#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time_parser
import json
import re
from caliper.server.run import parser_log

def unzip_parser(content, outfp):
    return time_parser.time_parser(content, outfp)

def unzip(filePath, outfp):
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

        tc = re.search("[\n\r]{2,}([\s\S]+?)\[status\]", case)
        if tc is not None:
            tableContent[parser_log.I_TABLE] = parser_log.parseTable(tc.groups()[0], "\\s{1,}")
            tableContent[parser_log.CENTER_TOP] = ""
            tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "unzip_output.log"
    outfile = "unzip_json.txt"
    outfp = open(outfile, "a+")
    unzip(infile, outfp)
    outfp.close()