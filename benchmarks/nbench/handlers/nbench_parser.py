#!/usr/bin/env python

import re
import yaml
import copy
import json
from caliper.server.run import parser_log

def parser(content, option, outfp):
    score = 0
    for lines in re.findall(
                    "=+LINUX\s+DATA\s+BELOW\s*=+\n(.*?)\n\*\s+Trademarks",
                    content,
                    re.DOTALL):
        if lines:
            line_list = lines.splitlines()
            for i in range(0, len(line_list)):
                if re.search("MEMORY\s+INDEX", line_list[i]):
                    memory_line = line_list[i]
                elif re.search("INTEGER\s+INDEX", line_list[i]):
                    int_line = line_list[i]
                else:
                    if re.search("FLOATING-POINT", line_list[i]):
                        float_line = line_list[i]
            if option == "int":
                line_list.remove(memory_line)
                line_list.remove(float_line)
                score = int_line.split(":")[1].strip()
            elif option == "float":
                line_list.remove(int_line)
                line_list.remove(memory_line)
                score = float_line.split(":")[1].strip()
            else:
                if option == "memory":
                    line_list.remove(int_line)
                    line_list.remove(float_line)
                    score = memory_line.split(":")[1].strip()

            for i in range(0, len(line_list)):
                outfp.write(line_list[i] + '\n')
            return score


def nbench_int_parser(content, outfp):
    score = -1
    score = parser(content, "int", outfp)
    return score


def nbench_float_parser(content, outfp):
    score = -1
    score = parser(content, "float", outfp)
    return score

dic = {}
dic['sincore_int'] = {}
dic['sincore_float'] = {}
int_list = ['NUMERIC SORT', 'STRING SORT', 'BITFIELD', 'FP EMULATION',
            'ASSIGNMENT', 'HUFFMAN', 'IDEA']
float_list = ['FOURIER', 'NEURAL NET', 'LU DECOMPOSITION']


def nbench_parser(content, outfp):
    for line in content.splitlines():
        get_value(line, 'sincore_int', int_list)
        get_value(line, 'sincore_float', float_list)
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic


def get_value(line, flag, list_tables):
    for label in list_tables:
        if re.search(label, line):
            value = re.findall('(\d+\.*\d*)', line)[0]
            dic[flag][label] = value
            break

def nbench(filePath, outfp):
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
        tc = re.search("(TEST[\s\S]+?)===", case)
        if tc is not None:
            table = []
            content = re.sub(":|-", "", tc.groups()[0])
            lines = content.splitlines()
            appendCells = []
            for appendCell in re.split("\\s{2,}", lines[1]):
                if appendCell.strip() != "":
                    appendCells.append(appendCell)
            for index, line in enumerate(lines):
                td = []
                cells = re.split("\\s{2,}", line)
                if index == 0:
                    for cellIndex, topCell in enumerate(cells):
                        if topCell.strip() != "":
                            if cellIndex >= 2:
                                td.append(topCell + " " + appendCells[cellIndex - 2])
                            else:
                                td.append(topCell)

                elif index != 1:
                    for cell in cells:
                        if cell.strip() != "":
                            td.append(cell.strip())
                if len(td) > 0:
                    table.append(td)

            tableContent[parser_log.CENTER_TOP] = ""
            tableContent[parser_log.TABLE] = table
            tables.append(copy.deepcopy(tableContent))

        original_group = re.search("(={4,}[\s\S]+?\n)([\s\S]+\n)={4,}", case)
        if original_group is not None:
            tableContent[parser_log.CENTER_TOP] = original_group.groups()[0]
            tableContent[parser_log.TABLE] = []
            tableContent[parser_log.I_TABLE] = parser_log.parseTable(original_group.groups()[1], ":")
            tables.append(copy.deepcopy(tableContent))
        linux_data_group = re.search("(={4,}[\s\S]+?\n){2}([\s\S]+Baseline[\s\S]+?\n)", case)
        if linux_data_group is not None:
            tableContent[parser_log.CENTER_TOP] = linux_data_group.groups()[0]
            tableContent[parser_log.TABLE] = []
            tableContent[parser_log.I_TABLE] = parser_log.parseTable(linux_data_group.groups()[1], ":")
            tables.append(copy.deepcopy(tableContent))
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "nbench_output.log"
    outfile = "nbench_json.txt"
    outfp = open(outfile, "a+")
    nbench(infile, outfp)
    outfp.close()
