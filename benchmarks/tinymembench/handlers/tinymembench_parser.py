import re
import sys
import math
import yaml
import json
import copy
from caliper.server.run import parser_log

def tinyResult(content, outfp):
	score = 0
	sum = 1.0
	i = 0
	avg_bandwidth = 0.0
	dic = {}
	dic['tiny_bandwidth'] = {}
	dic['tiny_bandwidth']['C_copy_backwards']  = []
	dic['tiny_bandwidth']['C_copy']  = []
	dic['tiny_bandwidth']['C_copy_prefetched_32B'] = []
	dic['tiny_bandwidth']['C_copy_prefetched_64B'] = []
	dic['tiny_bandwidth']['C_2-pass_copy'] = []
	dic['tiny_bandwidth']['C_2-pass_copy_prefetched_32B']  = []
        dic['tiny_bandwidth']['C_2-pass_copy_prefetched_64B']  = []
        dic['tiny_bandwidth']['C_fill'] = []
        dic['tiny_bandwidth']['standard_memcpy']  = []
        dic['tiny_bandwidth']['standard_memset']  = []
	dic['tiny_latency'] = {}
	dic['tiny_latency']['Hugepage_single_random_read']= []
	dic['tiny_latency']['Hugepage_dual_random_read'] = []
	dic['tiny_latency']['No_Hugepage_single_random_read'] = []
	dic['tiny_latency']['No_Hugepage_dual_random_read'] = []
	dic_list = ['C_copy_backwards','C_copy','C_copy_prefetched_32B','C_copy_prefetched_64B','C_2-pass_copy','C_2-pass_copy_prefetched_32B','C_2-pass_copy_prefetched_64B','C_fill','standard_memcpy','standard_memset']
	outfp.write('+++++++++++++++++++++++++++++MEMORY Bandwidth+++++++++++++++++++++++++++++++++\n')	
	outfp.write('OPERATIONS %54s' %': BANDWIDTH\n')

	outfp.write("%s\n" %(content.split("==========================================================================")[-3]))
	outfp.write('+++++++++++++++++++++++++++++MEMORY Latency+++++++++++++++++++++++++++++++++')
	outfp.write("%s\n" %(content.split("==========================================================================")[-1]))
	list = content.splitlines()
#	commands = ["C copy backwards                                     ","C copy                                               ","C copy prefetched (32 bytes step)                    ","C copy prefetched (64 bytes step)                    ","C 2-pass copy                                        ","C 2-pass copy prefetched (32 bytes step)             ","C 2-pass copy prefetched (64 bytes step)             ","C fill                                               ","standard memcpy","standard memset"]
	commands = ["C copy backwards   ","C copy      ","C copy prefetched (32 bytes step)    ","C copy prefetched (64 bytes step)    ","C 2-pass copy       ","C 2-pass copy prefetched (32 bytes step)     ","C 2-pass copy prefetched (64 bytes step)    ","C fill      ","standard memcpy","standard memset"]
	
	i=0
        for lines in list:
            for command in commands:
                if (command in lines):
                    for item in re.findall("(\d+\.\d+\s*)",lines):
                        item = int(item.split(".")[0])
                        if item > 100:
                            dic['tiny_bandwidth'][dic_list[i]] = item
                            i+=1
                    break
	sum = 1.0
	i = 0
	content1 = str(content.split("==========================================================================")[-1])
	final_list = re.findall("(\d+\.\d+\s*)",content1.split("block size : single random read / dual random read, [MADV_HUGEPAGE")[-2],re.DOTALL)
	#outfp.write(line)
	line = []*34
	for item in final_list:
		item = float(item)
		if item != 0:
			item = 100000/item
		line.append(item)
			
		
	lista = [line[12],line[14],line[16],line[18],line[20],line[22],line[24], line[26],line[28],line[30],line[32]]
	dic['tiny_latency']['Hugepage_single_random_read'] = lista
	listb = [line[13],line[15] ,line[17],line[19],line[21],line[23],line[25],line[27] ,line[29] ,line[31],line[33]]
	dic['tiny_latency']['Hugepage_dual_random_read'] = listb
	content1 = str(content.split("block size : single random read / dual random read, [MADV_HUGEPAGE")[-1])
        final_lis = re.findall("(\d+\.\d+\s*)",content1,re.DOTALL)
	line = []*34
	for item in final_list:
		item = float(item)
		if item != 0:
			item = 100000/item
		line.append(item)
	lista = [line[12],line[14],line[16],line[18],line[20],line[22],line[24], line[26],line[28],line[30],line[32]]
	dic['tiny_latency']['No_Hugepage_single_random_read'] = lista
	listb = [line[13],line[15] ,line[17],line[19],line[21],line[23],line[25],line[27] ,line[29] ,line[31],line[33]]
	dic['tiny_latency']['No_Hugepage_dual_random_read'] = listb
	return dic

def tinymembench_parser(content, outfp):
	score = -1
	score = tinyResult(content, outfp)


	return score


def tinymembench(filePath, outfp):
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

		tableContent2 = re.findall("={4,}\n==[\s\S]+?[\n\r]{3,}", case)
		for centerTop2 in tableContent2:
			top = re.search("={4,}\n[\s\S]+?={4,}", centerTop2)
			if top is not None:
				tableContent[parser_log.CENTER_TOP] = top.group(0)
			table2 = re.search("={4,}[\n\r]{2,}([\s\S]+?)[\n\r]{3,}", centerTop2)
			if table2 is not None:
				table2Content = re.sub("---", "", table2.groups()[0])
				tableContent[parser_log.I_TABLE] = parser_log.parseTable(table2Content, ":")
			tables.append(copy.deepcopy(tableContent))

		leftStr = re.sub("={4,}\n==[\s\S]+?[\n\r]{3,}", "", case)

		tableContent1 = re.findall("={4,}\n[\s\S]+?\[status\]", leftStr)
		for centerTop1 in tableContent1:
			top = re.search("={4,}\n[\s\S]+?={4,}", centerTop1)
			if top is not None:
				tableContent[parser_log.CENTER_TOP] = top.group(0)
			table1 = re.search("={4,}[\n\r]{2,}([\s\S]+?)[\n\r]{3,}", centerTop1)
			if table1 is not None:
				table1Content = re.sub("---", "", table1.groups()[0])
				tableContent[parser_log.I_TABLE] = parser_log.parseTable(table1Content, ":")
			tables.append(copy.deepcopy(tableContent))
		caseDict[parser_log.TABLES] = tables
		result.append(caseDict)
	outfp.write(json.dumps(result))
	return result


if __name__ == "__main__":
	infile = "tinymembench_output.log"
	outfile = "tinymembench_json.txt"
	outfp = open(outfile, "a+")
	tinymembench(infile, outfp)
	outfp.close()
