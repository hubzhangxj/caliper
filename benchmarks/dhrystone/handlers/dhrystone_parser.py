import re
import json
from caliper.server.parser_process import parser_log

def whets_parser(content, outfp):
    score = -1
    lines = content.splitlines()
    for i in range(0, len(lines)):
        if re.search("MWIPS", lines[i]):
            line = lines[i]
            fields = line.split()
            score = fields[1]
            outfp.write(str(score) + '\n')
    return score


def dhry2_parser(content, outfp):
    score = -1
    for line in re.findall("Dhrystones\s+per\s+Second:\s+(.*)\n", content):
        fields = line.split()
        score = fields[-1]
        outfp.write(str(score) + '\n')
        break
    return score

def dhrystone(filePath, outfp):
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
        centerTopGroup = re.search("Dhrystone Benchmark([\s\S]+)used in the benchmark:", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.group(0)
        tableGroup = re.search("used in the benchmark:\n([\s\S]+)\n\[status\]", case)
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
    infile = "dhrystone_output.log"
    outfile = "dhrystone_json.txt"
    outfp = open(outfile, "a+")
    dhrystone(infile, outfp)
    outfp.close()
