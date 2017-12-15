import re
import string
import pdb
import json
from caliper.server.run import parser_log

def redis_parser(content , outfp ):
#[test: Instance_2]

    for test_case in re.findall("\[test:\s+(.*?)\]", content):
	test_case_latency = test_case + "_latency"
	test_case_bandwidth = test_case + "_bandwidth"
  
    dic = {}
    dic[test_case_latency] = {}
    dic[test_case_bandwidth] = {}
    dic[test_case_latency]['short-lat'] = 0
    dic[test_case_latency]['basic-lat'] = 0
    dic[test_case_latency]['pipeline-lat'] = 0
    dic[test_case_bandwidth]['short-qps'] = 0
    dic[test_case_bandwidth]['basic-qps'] = 0
    dic[test_case_bandwidth]['pipeline-qps'] = 0

    short_count = 0
    basic_count = 0
    pipeline_count = 0
    for contents in re.findall("====== SHORT ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
         short_final = string.atof(contents.strip())
         outfp.write("short-qps = %s \n " %  short_final)
         dic[test_case_bandwidth]['short-qps'] += short_final

    for contents in re.findall("====== BASIC ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
        basic_final = string.atof(contents.strip())
        outfp.write("basic-qps = %s \n " % basic_final)
        dic[test_case_bandwidth]['basic-qps'] += basic_final

    for contents in re.findall("====== PIPELINE ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
        pipeline_final = string.atof(contents.strip())
        outfp.write("pipeline-qps = %s \n\n " % pipeline_final)
        dic[test_case_bandwidth]['pipeline-qps'] += pipeline_final

    for contents in re.findall("====== SHORT ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        short_final = string.atof(contents.strip())
        outfp.write("short-lat = %s \n " %  short_final)
        dic[test_case_latency]['short-lat'] += short_final
	short_count += 1

    for contents in re.findall("====== BASIC ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        basic_final = string.atof(contents.strip())
        outfp.write("basic-lat = %s \n " % basic_final)
        dic[test_case_latency]['basic-lat'] += basic_final
	basic_count += 1

    for contents in re.findall("====== PIPELINE ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        pipeline_final = string.atof(contents.strip())
        outfp.write("pipeline-lat = %s \n\n " % pipeline_final)
        dic[test_case_latency]['pipeline-lat'] += pipeline_final
	pipeline_count += 1

    if short_count != 0:
    	dic[test_case_latency]['short-lat'] = dic[test_case_latency]['short-lat'] / short_count

    if basic_count != 0:
    	dic[test_case_latency]['basic-lat'] = dic[test_case_latency]['basic-lat'] / basic_count

    if pipeline_count != 0:
    	dic[test_case_latency]['pipeline-lat'] = dic[test_case_latency]['pipeline-lat'] / pipeline_count

    if dic[test_case_bandwidth]['short-qps'] == 0:
	dic[test_case_bandwidth]['short-qps'] = -1

    if dic[test_case_bandwidth]['basic-qps'] == 0:
	dic[test_case_bandwidth]['basic-qps'] = -1

    if dic[test_case_bandwidth]['pipeline-qps'] == 0:
	dic[test_case_bandwidth]['pipeline-qps'] = -1

    if dic[test_case_latency]['short-lat'] == 0:
	dic[test_case_latency]['short-lat'] = -1

    if dic[test_case_latency]['basic-lat'] == 0:
	dic[test_case_latency]['basic-lat'] = -1

    if dic[test_case_latency]['pipeline-lat'] == 0:
	dic[test_case_latency]['pipeline-lat'] = -1

    return dic


def redis(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search('\[([\S\ ]+)\]\n', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)
            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        tables = []
        tableContent = {}
        #            centerTopGroup = re.search("(log\:[\S\ ]+\n)", case)
        #            tableContent[parser_log.CENTER_TOP] = centerTopGroup.groups()[0]
        tableGroup = re.search("(\=\=\=[\s\S]+)\[st", case)
        if tableGroup is not None:
            tableGroupContent_temp1 = tableGroup.groups()[0].strip()
            tableGroupContent_temp2 = re.sub(
                'Finish generate dump data[\s\S]+call redis-benchmark to test redis-0', '',
                tableGroupContent_temp1)
            tableGroupContent_temp3 = re.sub('[PIPELINE|SHORT][\S\ ]+', '', tableGroupContent_temp2)
        tableGroupContent = re.sub('\=\=\=+', '', tableGroupContent_temp3)
        table = parser_log.parseTable(tableGroupContent, "''{1,}")
        tableContent[parser_log.I_TABLE] = table
    tables.append(tableContent)
    caseDict[parser_log.TABLES] = tables
    result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "redis_output.log"
    outfile = "redis_json.txt"
    outfp = open(outfile, "a+")
    redis(infile, outfp)
    outfp.close()
