#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import importlib
import re
import logging
import subprocess
import yaml
import shutil
try:
    import common
except ImportError:
    import caliper.common as common
from caliper.server import crash_handle
from caliper.server.shared import error
from caliper.server import utils as server_utils
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder

TOP = "top"
BOTTOM = "bottom"
CENTER_TOP = "centerTop"
TABLES = "tables"
TABLE = "table"
I_TABLE = "i_table"

def parser_caliper_tests(sections, run_case_list):
    if not os.path.exists(Folder.exec_dir):
        print "Invalid Parser input Folder"
        return -1

    if not os.path.exists(Folder.results_dir):
        os.mkdir(Folder.results_dir)
    if not os.path.exists(Folder.yaml_dir):
        os.mkdir(Folder.yaml_dir)
    flag = 0
    try:
        get_test_config()
    except Exception,e:
        logging.info(e)
    try:
        logging.debug("beginnig to parse the test cases")
        test_result = parsing_run(sections, run_case_list)
    except error.CmdError:
        logging.info("There is wrong in parsing test cases")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag

def get_test_config():
    if not os.path.exists(Folder.json_dir):
        caliper_path.create_folder(Folder.json_dir)
    sh_path = os.path.join(os.environ['HOME'], '.caliper', 'get_hw_info', 'tests')
    os.chdir(sh_path)
    hosts_path = os.path.join(caliper_path.caliper_config_file, 'hosts')
    subprocess.call("ansible-playbook -i %s test.yml -e hosts=%s" % (hosts_path, caliper_path.sections[0]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shutil.copy('/tmp/config_output.json', os.path.join(Folder.json_dir, 'config_output.json'))

def parsing_run(sections, run_case_list):
    dic = {}
    for i in range(0, len(sections)):
        dic[sections[i]] = {}
        # try to resolve the configuration of the configuration file
        try:
            run_file = sections[i] + '_run.cfg'
            parser = sections[i] + '_parser.py'
        except Exception:
            raise AttributeError("The is no option value of parser")

        common.print_format()
        logging.info("Parsing %s" % sections[i])
        bench = os.path.join(caliper_path.BENCHS_DIR, sections[i], 'defaults')

        try:
            result = parse_all_cases(bench,sections[i], parser, dic, run_case_list)
        except Exception:
            logging.info("Parsing %s Exception" % sections[i])
            crash_handle.main()
            common.print_format()
            run_flag = server_utils.get_fault_tolerance_config(
                'fault_tolerance', 'run_error_continue')
            if run_flag == 1:
                continue
            else:
                return result
        else:
            logging.info("Parsing %s Finished" % sections[i])
            common.print_format()
        try:
            logging.info("Parsing json %s" % sections[i])
            log_bench = os.path.join(Folder.exec_dir, sections[i])
            logfile = log_bench + "_output.log"
            parser_json(sections[i],  parser, logfile)
        except Exception as e:
            logging.info(e)
        else:
            logging.info("Parsing json %s Finished" % sections[i])

    outfp = open(os.path.join(caliper_path.folder_ope.workspace,
                              caliper_path.folder_ope.name.strip()
                              + "/final_parsing_logs.yaml"), 'w')
    outfp.write(yaml.dump(dic, default_flow_style=False))
    outfp.close()
    return 0

def parse_all_cases(kind_bench, bench_name, parser_file, dic, run_case_list):
    """
    function: parse one benchmark which was selected in the configuration files
    """
    try:
        # get the abspath, which is filename of run config for the benchmark
        # get the config sections for the benchmrk
        bench_conf_file = os.path.join(kind_bench, 'main.yml')
        # get the config sections for the benchmrk
        pf = open(bench_conf_file, 'r')
        values = yaml.load(pf.read())
        sections_run = values[bench_name].keys()
    except AttributeError as e:
        raise AttributeError
    except Exception:
        raise
    logging.debug("the sections to run are: %s" % sections_run)
    if not os.path.exists(Folder.exec_dir):
        os.mkdir(Folder.exec_dir)
    log_bench = os.path.join(Folder.exec_dir, bench_name)
    logfile = log_bench + "_output.log"
    tmp_log_file = log_bench + "_output_tmp.log"
    parser_result_file = log_bench + "_parser.log"
    tmp_parser_file = log_bench + "_parser_tmp.log"
    if os.path.exists(parser_result_file):
        os.remove(parser_result_file)
    # for each command in run config file, read the config for the benchmark
    i = 0
    for section in sections_run:
        if section in run_case_list:
            dic[bench_name][section] = {}
            flag = 0
            try:
                parser = values[bench_name][section]['parser']
            except Exception:
                logging.debug("no value for the %s" % section)
                continue
            if os.path.exists(tmp_parser_file):
                os.remove(tmp_parser_file)
            # parser the result in the tmp_log_file, the result is the output of
            # running the command
            try:
                logging.debug("Parsering the result of command: %s" % section)
                outfp = open(logfile, 'r')
                infp = open(tmp_log_file, 'w')
                # infp.write(re.findall("test start\s+%+(.*?)%+\s+test_end", outfp.read(), re.DOTALL)[sections_run.index(section) - i])
                infp.write(re.findall(section + "\s+test start\s+%+(.*?)%+\s+test_end", outfp.read(), re.DOTALL)[-1])
                infp.close()
                outfp.close()
                parser_result = parser_case(bench_name, parser_file,
                                            parser, tmp_log_file,
                                            tmp_parser_file)
                dic[bench_name][section]["type"] = type(parser_result)
                dic[bench_name][section]["value"] = parser_result
            except Exception, e:
                logging.info("Error while parsing the result of \" %s \""
                             % section)
                logging.info(e)
                if os.path.exists(tmp_parser_file):
                    os.remove(tmp_parser_file)
                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
            else:
                server_utils.file_copy(parser_result_file, tmp_parser_file, "a+")
                if os.path.exists(tmp_parser_file):
                    os.remove(tmp_parser_file)
                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
                if (parser_result <= 0):
                    continue
        else:
            i += 1
            continue

def parser_case(bench_name, parser_file, parser, infile, outfile):
    if not os.path.exists(infile):
        return -1
    fp = open(outfile, 'a+')
    # the parser function defined in the config file is to filter the output.
    # get the abspth of the parser.py which is defined in the config files.
    # changed by Elaine Aug 8-10
    if not parser_file:
        pwd_file = bench_name + "_parser.py"
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', pwd_file)
    else:
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', parser_file)
    rel_path = bench_name + "_parser.py"
    parser_name = rel_path.replace('.py', '')
    handlers_path = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers')
    sys.path.append(handlers_path)

    result = 0
    if os.path.isfile(parser_file):
        try:
            # import the parser module import_module
            parser_module = importlib.import_module(parser_name)
        except ImportError, e:
            logging.info(e)
            return -3
        try:
            methodToCall = getattr(parser_module, parser)
        except Exception, e:
            logging.info(e)
            return -4
        else:
            infp = open(infile, "r")
            outfp = open(outfile, 'a+')
            contents = infp.read()
            for content in re.findall("BEGIN TEST(.*?)\[status\]", contents,
                                      re.DOTALL):
                try:
                    # call the parser function to filter the output
                    logging.debug("Begining to parser the result of the case")
                    result = methodToCall(content, outfp)
                except Exception, e:
                    logging.info(e)
                    return -5
            outfp.close()
            infp.close()
    fp.close()
    return result

def parser_json(bench_name, parser_file, infile):
    if not os.path.exists(Folder.json_dir):
        os.mkdir(Folder.json_dir)
    outfile_name = bench_name +'_json.txt'
    outfile = os.path.join(Folder.json_dir, outfile_name)
    if not parser_file:
        pwd_file = bench_name + "_parser.py"
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', pwd_file)
    else:
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', parser_file)
    rel_path = bench_name + "_parser.py"
    parser_name = rel_path.replace('.py', '')
    handlers_path = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers')
    sys.path.append(handlers_path)

    result = 0
    if os.path.isfile(parser_file):
        try:
            # import the parser module import_module
            parser_module = importlib.import_module(parser_name)
        except ImportError, e:
            logging.info(e)
            return -3
        try:
            methodToCall = getattr(parser_module, bench_name)
        except Exception, e:
            logging.info(e)
            return -4
        else:
            outfp = open(outfile, 'a+')
            try:
                # call the parser function to filter the output
                logging.debug("Begining to parser the result of the case")
                result = methodToCall(infile, outfp)
            except Exception, e:
                logging.info(e)
                return -5
            outfp.close()
    return result

def parseData(filePath):
    file = open(filePath)
    filecontent = file.read()
    file.close()
    cases = re.findall('<<<BEGIN TEST>>>([\s\S]+?)<<<END>>>', filecontent)
    return cases

def getBottom(case):
    endGroup = re.search('\[status\]([\s\S]+)Time in Seconds([\s\S]+)s', case)
    if endGroup != None:
        return endGroup.group(0)
    return None

def parseTable(content, spiltStr, maxsplit=0):
    table = []
    for line in content.splitlines():
        cells = re.split(spiltStr, line, maxsplit)
        td = []
        for cell in cells:
            if cell.strip() != "":
                td.append(cell.strip())
        if len(td) > 0:
            table.append(td)
    return table

def parseMergeTable(content, spiltStr, merges, excludes=[], adds=[], maxsplit=0, ):
    '''
    按行分割内容,每行进行split,最终放回一个table 数组
    支持对split后的数据进行部分合并
    :param content:  内容
    :param spiltStr: 正则表达式
    :param merges:  需要合并的列 结构[[1,2]](从1开始)
    :param excludes: 排除第几行 (从1开始)
    :param adds: 在某行的某个位置添加一个td [[第几行,第几列]]
    :param maxsplit: 最大分割数
    :return: [[td][td]]
    '''
    table = []
    for i, line in enumerate(content.splitlines()):
        cells = re.split(spiltStr, line.strip(), maxsplit)
        td = []
        for index, cell in enumerate(cells):
            if cell.strip() != "":
                td.append(cell.strip())

        if len(td) > 0:
            if i + 1 not in excludes:
                newTd = []
                for id, t in enumerate(td):
                    newString = ""
                    begin = -1
                    end = -1
                    for merge in merges:
                        begin = merge[0] - 1
                        end = merge[1] - 1
                        if id == begin:
                            newString = td[begin] + " " + td[end]
                            break
                        if id == end:
                            break
                    if id == begin:
                        newTd.append(newString)
                    elif id == end:
                        continue
                    else:
                        newTd.append(t)
                    for addCellId in adds:
                        addLine = addCellId[0]
                        addCell = addCellId[1]
                        if i == addLine - 1 and len(newTd) == addCell - 1:
                            newTd.append("")
                table.append(newTd)
            else:
                for addCellId in adds:
                    addLine = addCellId[0]
                    addCell = addCellId[1]
                    if i == addLine - 1 and len(td) == addCell - 1:
                        td.append("")
                table.append(td)
    return table

def parseMergeTitleTable(content, spiltStr, merges, title_merges, excludes=[], adds=[], maxsplit=0, ):
    '''
    按行分割内容,每行进行split,最终放回一个table 数组
    支持对split后的数据进行部分合并
    :param content:  内容
    :param spiltStr: 正则表达式
    :param merges:  需要合并的列 结构[[1,2]](从1开始)
    :param excludes: 排除第几行 (从1开始)
    :param adds: 在某行的某个位置添加一个td [[第几行,第几列]]
    :param maxsplit: 最大分割数
    :return: [[td][td]]
    '''
    table = []
    for i, line in enumerate(content.splitlines()):
        cells = re.split(spiltStr, line.strip(), maxsplit)
        td = []
        for index, cell in enumerate(cells):
            if cell.strip() != "":
                td.append(cell.strip())

        if len(td) > 0:
            if i + 1 not in excludes:
                newTd = []
                for id, t in enumerate(td):
                    if i == 0:
                        newString = ""
                        begin = -1
                        end = -1
                        for merge in title_merges:
                            begin = merge[0] - 1
                            end = merge[1] - 1
                            if id == begin:
                                newString = td[begin] + " " + td[end]
                                break
                            if id == end:
                                break
                        if id == begin:
                            newTd.append(newString)
                        elif id == end:
                            continue
                        else:
                            newTd.append(t)
                    else:
                        newString = ""
                        begin = -1
                        end = -1
                        for merge in merges:
                            begin = merge[0] - 1
                            end = merge[1] - 1
                            if begin >= len(td) or end >= len(td):
                                break
                            if id == begin:
                                newString = td[begin] + " " + td[end]
                                break
                            if id == end:
                                break
                        if id == begin:
                            newTd.append(newString)
                        elif id == end:
                            continue
                        else:
                            newTd.append(t)
                    for addCellId in adds:
                        addLine = addCellId[0]
                        addCell = addCellId[1]
                        if i == addLine - 1 and len(newTd) == addCell - 1:
                            newTd.append("")
                table.append(newTd)
            else:
                for addCellId in adds:
                    addLine = addCellId[0]
                    addCell = addCellId[1]
                    if i == addLine - 1 and len(td) == addCell - 1:
                        td.append("")
                table.append(td)
    return table