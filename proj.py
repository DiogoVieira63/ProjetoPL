
import re
from textwrap import indent
from typing import final
import ply.lex as lex

import json
import statistics



tokens = ["SKIP","SEP","TEXT","NEWLINE","MULT","FUNC"]


states = [
    ("header","exclusive")
]

def t_header_SKIP(t):
    r'(,{2,}\n*|,\n)'
    if '\n' in t.value:
        t_header_NEWLINE(t)



def t_SKIP(t):
    r'(,{2,}\n*|,\n)'
    match = t.value
    count = (match.count(',')) + ('\n' in match) -1
    for i in range(count):
        t.lexer.line.append(None)
    if '\n' in match:
        t_NEWLINE(t)


def t_header_FUNC(t):
    r'::(?P<func>\w+)'
    func = (t.lexer.lexmatch.group('func'))
    last = t.lexer.header[-1]
    if last[2] is not []:
        last[2].append(func)
    else:
        t.lexer.header[-1]=(last[0],last[1],[func])


def t_ANY_SEP(t):
    r','


def t_header_MULT(t):
    r'{(?P<number>\d+)(,(?P<number2>\d+))?}'
    match = t.lexer.lexmatch
    if match.group('number2') is not None:
        value= int(match.group('number2'))
    else:
        value= int(match.group('number'))

    elem = lexer.header[-1]
    lexer.header[-1]=(elem[0],value,[])

def t_header_TEXT(t):
    r'(?![ \t]+$)(["\'].+["\']|[^{},\n]+)'
    t.value = re.sub(r'["\']',"",t.value)
    t.lexer.header.append((t.value,1,[]))

def t_TEXT(t):
    r'(?![ \t]+$)(".+"|[^,\n]+)'
    t.lexer.line.append(t.value)

def t_header_NEWLINE(t):
    r'\n'
    t.lexer.begin("INITIAL")

def t_NEWLINE(t):
    r'\n'
    t.lexer.values.append(t.lexer.line)
    t.lexer.line=[]


def t_ANY_error(t):
    print("Error")

lexer = lex.lex()
lexer.header=[]
lexer.values=[]
lexer.line=[]

lexer.begin("header")

file = "testes/emd"

f = open(file +".csv","r")

texto = f.read()

lexer.input(texto)


for tok in lexer:
    print(tok)


print(lexer.header)
#print(lexer.values)


def doFunc(func,list):
    list = [float(i) for i in list]
    if func == "sum":
        return sum(list)
    elif func == "media":
        return sum(list)/len(list)
    elif func == "median":
        return statistics.median(list)
    elif func== "mode":
        return statistics.mode(list)
    elif func== "range":
        return max(list)-min(list)  



listDict=[]
for listLine in lexer.values:
    dictLine = dict()
    indexLine=0
    for (header,hNum,other) in lexer.header:
        if (hNum == 1):
            if listLine[indexLine] is not None:
                dictLine[header]=listLine[indexLine]
            indexLine+=1
        else: 
            list=[]
            for i in range(hNum):
                if listLine[indexLine+i] is not None :
                    list.append(listLine[indexLine+i])
                else:
                    break
            indexLine+=hNum
            if other != []:
                for func in other:
                    dictLine[header+"_"+func]=doFunc(func,list)
            else:
                dictLine[header]=list
    listDict.append(dictLine)

indent =4

def spaces(n):
    return " " *(indent *n)

def writeDict(listDict):
    finalStr= "[\n"
    for indexDict,dict in enumerate(listDict):
        finalStr+=spaces(1)
        finalStr+="{\n"
        for index,(key,elem) in enumerate(dict.items()):
            finalStr+=spaces(2)
            if type(elem) is str:
                finalStr+=f'"{key}": "{elem}"'
            elif type(elem) is int or type(elem) is float:
                finalStr+=f'"{key}": {elem}'
            else:
                finalStr+='"' + key + '": '
                finalStr+="["
                finalStr+=",".join(map(str,list))
                finalStr+="]\n" 

            if index != len(dict)-1:
                finalStr+=","
            finalStr+="\n"  
        finalStr+=spaces(1)
        finalStr+="}"
        if indexDict != len(listDict)-1:
            finalStr+=","
        finalStr+="\n"
    finalStr+="]\n"
    return finalStr

print(listDict)

y = writeDict(listDict)

# convert into JSON:
#y = json.dumps(listDict, indent=4,ensure_ascii=False)

f.close()

f = open(file + ".json","w")

f.write(y)

f.close()


