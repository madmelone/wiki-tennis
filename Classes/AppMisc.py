# Various small scripts that take input text and return output text

import re

def ReverseTable(data):
    # Reverses the order of a wikimedia table. Can handle merged rows, but only in first column
    data = "\n".join([f.strip() for f in data.split("\n")])
    end = data[data.index("|}"):]
    data = data[:data.index("|}")].split("|-\n")
    data = data[:2] + data[2:][::-1]
    for c, d in enumerate(data):
        if "rowspan=" in d:
            num = re.search("(rowspan=)\"*\d{1,}", d).group()
            num = int(num[num.index('=')+1:].replace('"', ""))
            if num > 1:
                pipes = []
                brackets = 0
                for e, f in enumerate(d):
                    if f == "{" or f == "[": # ignore pipes in wikilinks and template calls
                        brackets += 1
                    elif f == "}" or f == "]":
                        brackets -= 1
                    if f == "|" and brackets == 0:
                        pipes.append(e)
                index = 1 if "!" in d else 2
                data[c] = d[pipes[index]:]
                data[c-num+1] = d[:pipes[index]] + data[c-num+1]
    return "|-\n".join(data) + end

def GetMisc(script, input):
    if script == "reverse":
        return ReverseTable(input)
    return ""
