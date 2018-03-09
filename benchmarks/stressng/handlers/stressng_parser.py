import re
import json
from caliper.server.parser_process import parser_log

def stress_ng_parser(content,outfp):
    result = 0
    if re.search(r'stress-ng: info:\s+\[[0-9]+\]\scpu\s+\d+\s+(\d+\.\d+).*',content):
        real_time = re.search(r'stress-ng: info:\s+\[[0-9]+\]\scpu\s+\d+\s+(\d+\.\d+).*',content)
        result =  real_time.group(1)
    outfp.write(content)
    return result 

def stressng(filePath, outfp):

    cases = parser_log.parseData(filePath)
    result = []
    for case in cases:
        caseDict = {}
        titleGroup = re.search('\[test:([\s\S]+)stress-', case)
        if titleGroup != None:
            caseDict[parser_log.TOP] = titleGroup.group(0)

            caseDict[parser_log.BOTTOM] = parser_log.getBottom(case)

        my_regex = '%s([\s\S]+)\[status\]:' % ("stress-")
        center = re.search(my_regex, case)
        table_contents = []
        if center != None:
            tableDict = {}
            data = center.group(1).strip()
            topstr_group = re.search("stress[\s\S]+?\[[\d]+\]([\s\S]+\n)stress-ng: info: \[\d+\] stressor", data)
            if topstr_group is not None:
                topstr = topstr_group.groups()[0]
                top = re.sub("stress([\s\S]+?)\[[\d]+\] ", "", topstr.strip())
                tableDict[parser_log.CENTER_TOP] = top

            lines = data.splitlines()
            isTop = True
            table = []
            td = ['stressor', 'bogo ops', 'real time(secs)', 'usr time(secs)', 'sys time(secs)',
                  'bogo ops/s(real time)', 'bogo ops/s(usr+sys time)']
            table.append(td)
            for line in lines:
                values = []
                if not isTop:
                    value = re.sub("stress([\s\S]+?)\[[\d]+\]", "", line)
                    cells = value.split(" ")
                    for table_title in cells:
                        title = table_title.strip()
                        if title != '':
                            values.append(title)

                if line.endswith("time)"):
                    isTop = False
                if len(values) != 0:
                    table.append(values)
            tableDict[parser_log.TABLE] = table
            table_contents.append(tableDict)
            caseDict[parser_log.TABLES] = table_contents
        result.append(caseDict)
    result = json.dumps(result)
    outfp.write(result)
    return result

if __name__ == "__main__":
    infile = "stressng_output.log"
    outfile = "stressng_json.txt"
    outfp = open(outfile, "a+")
    stressng(infile, outfp)
    # parser1(content, outfp)
    outfp.close()

