#!/usr/bin/python

import re
import string
import pdb
import json
from caliper.server.run import parser_log

def compute_mflops(content, outfp):
    score = 0
    # pdb.set_trace()
    for lines in re.findall("Reps(.*?)\n(.*?)\n([\d\.\%\s]*)", content,
                            re.DOTALL):
        mflops = 0
        line = lines[2].strip().split("\n")
        for i in range(0, len(line)):
            if (line[i] != ""):
                try:
                    mflops_tmp = string.atof(line[i].strip().split(" ")[-1])
                except Exception, e:
                    print e
                    continue
                else:
                    mflops = mflops + mflops_tmp
        mflops = mflops/len(line)
        outfp.write(str(mflops) + "\n")
        score = mflops
    return score


def linpack_dp_parser(content, outfp):
    score = -1
    if re.search("LINPACK(.*?)Double(.*?)", content, re.DOTALL):
        score = compute_mflops(content, outfp)
    return score


def linpack_sp_parser(content, outfp):
    score = -1
    if re.search("LINPACK(.*?)Single(.*?)", content, re.DOTALL):
        score = compute_mflops(content, outfp)
    return score

def linpack(filePath, outfp):
    file = open(filePath)
    filecontent = file.read()
    file.close()
    result = []
    cases = re.findall('<<<BEGIN TEST>>>([\s\S]+?)<<<END>>>', filecontent)
    for case in cases:
        caseDict = {}
        titleGroup = re.search('Memory required:([\s\S]+)performance:', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)

        endGroup = re.search('\[status\]([\s\S]+)Time in Seconds([\s\S]+)s', case)
        if endGroup != None:
            caseDict[parser_log.BOTTOM] = endGroup.group(0)

        my_regex = '%s([\s\S]+)\[status\]:' % (caseDict["top"])
        center = re.search(my_regex, case)
        table_contents = []
        if center != None:
            tableDict = {}
            data = center.group(1).strip()
            lines = data.splitlines()
            table = []
            for index in range(len(lines)):
                line = lines[index]
                newline = line.strip()
                if newline != '':
                    td = []
                    cells = newline.split(" ")
                    for table_title in cells:
                        title = table_title.strip()
                        if title != '':
                            td.append(title)
                    if len(td) > 1:
                        table.append(td)
            tableDict[parser_log.TABLE] = table
            table_contents.append(tableDict)
            caseDict[parser_log.TABLES] = table_contents
        result.append(caseDict)
    result = json.dumps(result)
    outfp.write(result)
    return result

if __name__ == "__main__":
    infile = "linpack_output.log"
    outfile = "linpack_json.txt"
    outfp = open(outfile, "a+")
    linpack(infile, outfp)
    # parser1(content, outfp)
    outfp.close()
