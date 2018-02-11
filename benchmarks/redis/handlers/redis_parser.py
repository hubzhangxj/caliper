import re
import string
import yaml
import json
from caliper.server.parser_process import parser_log


def redis_parser(content, outfp):
    # [test: Instance_2]

    for test_case in re.findall("\[test:\s+(.*?)\]", content):
        test_case_bandwidth = test_case

    dic = {}
    dic[test_case_bandwidth] = {}
    dic[test_case_bandwidth]['short-qps'] = 0
    dic[test_case_bandwidth]['basic-qps'] = 0
    dic[test_case_bandwidth]['pipeline-qps'] = 0

    for contents in re.findall("Short case\nqps:.*?(\d+.\d+), lat:", content, re.DOTALL):
        short_final = string.atof(contents.strip())
        outfp.write("short-qps = %s \n " % short_final)
        dic[test_case_bandwidth]['short-qps'] += short_final

    for contents in re.findall("Basic case\nqps:.*?(\d+.\d+), lat:", content, re.DOTALL):
        basic_final = string.atof(contents.strip())
        outfp.write("basic-qps = %s \n " % basic_final)
        dic[test_case_bandwidth]['basic-qps'] += basic_final

    for contents in re.findall("Pipeline case\nqps:.*?(\d+.\d+), lat:", content, re.DOTALL):
        pipeline_final = string.atof(contents.strip())
        outfp.write("pipeline-qps = %s \n\n " % pipeline_final)
        dic[test_case_bandwidth]['pipeline-qps'] += pipeline_final

    if dic[test_case_bandwidth]['short-qps'] == 0:
        dic[test_case_bandwidth]['short-qps'] = -1

    if dic[test_case_bandwidth]['basic-qps'] == 0:
        dic[test_case_bandwidth]['basic-qps'] = -1

    if dic[test_case_bandwidth]['pipeline-qps'] == 0:
        dic[test_case_bandwidth]['pipeline-qps'] = -1

    return dic


def redis(filePath, outfp):
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
        centerTopGroup = re.search("log:([\s\S]+?)\n", case)
        tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("Short case([\s\S]+)status", case)
        if tableGroup is not None:
            tableGroupContent_temp = tableGroup.groups()[0].strip().replace('[', '')
            tableGroupContent = re.sub('=', ':', tableGroupContent_temp)
            tableGroupContent = re.sub('lat:', 'lat=', tableGroupContent)
            table = parser_log.parseTable(tableGroupContent, ":{1,}")
            tableContent[parser_log.I_TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result


if __name__ == "__main__":
    infp = open("redis_output.log", "r")
    content = infp.read()
    content = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>', content, re.DOTALL)
    outfp = open("2.txt", "a+")
    for data in content:
        a = redis_parser(data, outfp)
    outfp.close()
    infp.close()
    infile = "redis_output.log"
    outfile = "redis.json"
    outfp = open(outfile, "a+")
    redis(infile, outfp)
    outfp.close()
