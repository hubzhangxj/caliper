#!/usr/bin/env python

import os
import sys
import importlib
import re
import logging

import yaml
try:
    import common
except ImportError:
    import caliper.common as common
from caliper.server import crash_handle
from caliper.server.shared import error
from caliper.server import utils as server_utils
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder

def parser_caliper_tests(flag):
    # f_option =1 if -f is used
    if not os.path.exists(Folder.exec_dir):
        print "Invalid Parser input Folder"
        return -1

    if not os.path.exists(Folder.results_dir):
        os.mkdir(Folder.results_dir)
    if not os.path.exists(Folder.yaml_dir):
        os.mkdir(Folder.yaml_dir)
    if not os.path.exists(Folder.html_dir):
        os.mkdir(Folder.html_dir)
    flag = 0
    try:
        logging.debug("beginnig to parse the test cases")
        test_result = parsing_run()
    except error.CmdError:
        logging.info("There is wrong in parsing test cases")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag

def parsing_run():
    # get the test cases defined files
    sections, run_case_list = common.read_config()
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
                command = values[bench_name][section]['command']
            except Exception:
                logging.debug("no value for the %s" % section)
                continue
            if os.path.exists(tmp_parser_file):
                os.remove(tmp_parser_file)
            # parser the result in the tmp_log_file, the result is the output of
            # running the command
            try:
                logging.debug("Parsering the result of command: %s" % command)
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