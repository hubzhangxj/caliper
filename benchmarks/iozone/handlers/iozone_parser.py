import re
import pdb
import json
from caliper.server.run import parser_log

def parser(content, outfp):
    score = 0
    for version in re.findall("(Iozone:.*Version.*?)\s+\n", content,
                        re.DOTALL):
        outfp.write(version)
        outfp.write("\n")

    for results in re.findall("(File\s+size.*)", content, re.DOTALL):
        outfp.write(results)
        outfp.write("\n")

    keywords = ['write', 'rewrite', 'read', 'reread', 'random_read',
            'random_write', 'bkwd_read', 'recored_rewrite', 'stride_read',
            'fwrite', 'frewrite', 'fread', 'freread']
    dic = {'write': 0, 'rewrite': 0, 'read': 0, 'reread': 0, 'random_read': 0,
            'random_write': 0, 'bkwd_read': 0, 'recored_rewrite': 0,
            'stride_read': 0, 'fwrite': 0, 'frewrite': 0, 'fread': 0,
            'freread': 0}

    if re.search("iozone\s+test\s+complete", content):
        for line in re.findall("(\d+\s+\d+\s+\d+\s+.*?)\niozone\s+test",
                                content, re.DOTALL):
            fields = line.split()
            for i in range(0, len(keywords)):
                try:
                    score = fields[i+2]
                except Exception, e:
                    print e
                    score = 0
                dic[keywords[i]] = score
                outfp.write(keywords[i] + ": "+score+"\n")
    return dic


def iozone_parser(content, outfp):
    return parser(content, outfp)

def iozone(filePath, outfp):
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
        centerTopGroup = re.search("\\\t{1,}Run began:[\s\S]+?File stride[\s\S]+?[\n\r]", case)
        if centerTopGroup is not None:
            tableContent[parser_log.CENTER_TOP] = centerTopGroup.group(0)
        tableGroup = re.search("ecord size.([\s\S]+)iozone", case)
        if tableGroup is not None:
            tableGroupContent = tableGroup.groups()[0].strip()
            lines = tableGroupContent.splitlines()
            table = []
            cellTop = []
            for lineIndex, line in enumerate(lines):
                if line.strip() != "":
                    td = []
                    cells = re.split("\\s{1,}", line.strip())

                    if lineIndex == 0:
                        for index, cell in enumerate(cells):
                            cellTop.append(cell.strip())
                    elif lineIndex == 1:
                        for index, cell in enumerate(cells):
                            if index >= 6 and index <= 10: 
                                td.append(cellTop[index - 6] + " " + cell.strip())
                            else:
                                td.append(cell.strip())
                        table.append(td)
                    else:
                        for index, cell in enumerate(cells):
                            td.append(cell.strip())
                        table.append(td)
            tableContent[parser_log.TABLE] = table
        tables.append(tableContent)
        caseDict[parser_log.TABLES] = tables
        result.append(caseDict)
    outfp.write(json.dumps(result))
    return result


if __name__ == "__main__":
    infile = "iozone_output.log"
    outfile = "iozone_json.txt"
    outfp = open(outfile, "a+")
    iozone(infile, outfp)
    outfp.close()
