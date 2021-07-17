# Various small scripts that take input text and return output text

import re

def ReverseTable(data):
    # Reverses the order of a wikimedia table. Can handle merged rows, but only in first column
    if data.count("|}") - data.count("|}}") == 1 and "wikitable" in data:
        data = [f.strip().replace("↓", "↑") for f in data.split("\n")]
        headers = [c for c,v in enumerate(data) if v != "" and v[0] == "!"]
        start_index = headers[-1] + 1
        for i,j in enumerate(headers,headers[0]):
            if  i != j:
                start_index = j - 1
                break
        start = "\n".join(data[:start_index])
        data = "\n".join(data[start_index:])
        end_index = list(set([m.start() for m in re.finditer('\|}', data)]) - set([m.start() for m in re.finditer('\|}}', data)]))[0]
        end = data[end_index:]
        data = [f for f in data[:end_index].split("|-\n")[::-1] if f != ""]
        for c, d in enumerate(data):
            if "rowspan=" in d: # merged rows
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
                    row = 0 if c - num + 1 < 0 else c - num + 1
                    data[row] = d[:pipes[index]] + data[row]
        return start + "\n|-\n" + "|-\n".join(data) + end
    else:
        return "Error: input does not contain a wikitable, or input contains more than one wikitable"

def GetMisc(script, input):
    if script == "reverse":
        return ReverseTable(input)
    return ""
