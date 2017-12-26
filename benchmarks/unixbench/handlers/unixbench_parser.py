import re
import yaml
import json
from caliper.server.run import parser_log

def unixbench_parser(contents, outfp):
    seperators ={'ub_Dhrystone':'Dhrystone 2 using register variables',
                 'ub_Whetstone':'Double-Precision Whetstone',
                 'ub_Execl_Throughput':'Execl Throughput',
                 'ub_File_Cpy_1024buf_2000blk':'File Copy 1024 bufsize 2000 maxblocks',
                 'ub_File_Cpy_256buf_500blk':'File Copy 256 bufsize 500 maxblocks',
                 'ub_File_Cpy_4096buf_8000blk':'File Copy 4096 bufsize 8000 maxblocks',
                 'ub_pipe_Throughput':'Pipe Throughput',
                 'ub_pipe_ctx':'Pipe-based Context Switching',
                 'ub_Process_Creation':'Process Creation',
                 'ub_shell_script_1_concurrent':'Shell Scripts \(1 concurrent\)',
                 'ub_shell_script_8_concurrent':'Shell Scripts \(8 concurrent\)'}
    contents = contents.split("-----------------------------------------------------------------------")

    dic = {}
    dic['cpu_multicore'] = {}
    dic['cpu_multicore']['multicore_unixbench'] = {}
    dic['cpu_sincore'] = {}
    dic['cpu_sincore']['sincore_unixbench'] = {}
    for key,value in seperators.iteritems():
        dic['cpu_sincore']['sincore_unixbench'][key] = re.findall(value + r'\s+\d+.\d+\s+(\d+.\d+)',contents[1])[0]
        dic['cpu_multicore']['multicore_unixbench'][key] = re.findall(value + r'\s+\d+.\d+\s+(\d+.\d+)', contents[2])[0]

    outfp.write(yaml.dump(dic,default_flow_style=False))
    outfp.close()
    return dic

def unixbench(filePath, outfp):
    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)
        titleGroup = re.search("={4,}([\s\S]+?)-{4,}", case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)

        table_content_groups = re.findall("-{4,}([\s\S]+)\[status\]", case)
        contents = re.split("-{4,}", table_content_groups[0])
        table_contents = []
        for content in contents:
            contentDict = {}
            centerTopGroup = re.search("Benchmark Run([\s\S]+)samples\)", content)
            if centerTopGroup is not None:
                contentDict[parser_log.CENTER_TOP] = centerTopGroup.group(0)
            tableContentGroup = re.search("System Benchmarks([\s\S]+)[\d+]", content)
            if tableContentGroup is not None:
                tableContent = tableContentGroup.group(0)
                table = []
                for line in tableContent.splitlines():
                    cells = re.split(" {2,}", line)
                    td = []

                    if "========" in line:
                        continue
                    if len(cells) > 2:
                        for cell in cells:
                            realCell = cell.strip()
                            if realCell is not "" and realCell != "========":
                                td.append(realCell)
                    elif len(cells) > 1:
                        td.append(cells[0])
                        td.append("")
                        td.append("")
                        td.append(cells[1])
                    else:
                        td.append(cells[0])
                        td.append("")
                        td.append("")

                    if len(td) > 0:
                        table.append(td)
                contentDict[parser_log.TABLE] = table
            table_contents.append(contentDict)
        caseDict[parser_log.TABLES] = table_contents
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result

if __name__ == "__main__":
    infile = "unixbench_output.log"
    outfile = "unixbench_json.txt"
    outfp = open(outfile, "a+")
    unixbench(infile, outfp)
    # parser1(content, outfp)
    outfp.close()