import ply.yacc as yacc
from projLex import tokens, literals 
import re
from projUtils import *


def p_Program (p):
    "Program : Fases "

def p_Fases_list (p):
    "Fases : Fases Fase"

def p_Fases (p):
    "Fases : Fase"

def p_Fase (p):
    "Fase : '%' '%' FactorFase"

def p_Fase_end (p):
    "Fase : allNoConv"
    p.parser.noConv = p[1][2:]


def p_FactorFase_list (p):
    "FactorFase : FaseId Group"

def p_FaseId_lex(p):
    "FaseId : LEX"
    p.parser.current = p.parser.lex


def p_FaseId_yacc(p):
    "FaseId : YACC"
    p.parser.current = p.parser.yacc


def p_Group(p):
    "Group : Declarations Rules"


def p_Declarations_list(p):
    "Declarations : Declarations Declaration"

def p_Declarations_Empty(p):
    "Declarations :  "


def p_Declaration(p):
    "Declaration : '%' TypeDeclaration '=' Attrib"
    p.parser.current[0][p[2]] = p[4] 

def p_Declaration_Comment(p):
    "Declaration : COMMENT"
    p.parser.current[1][p[1]] = ""


def p_Declaration_Var(p):
    "Declaration : str '=' Var"
    p.parser.current[1][p[1]] = p[3]

def p_Var_Single(p):
    "Var : Elem"
    p[0] = p[1]

def p_Var_DictEmpty(p):
    "Var : allBraces"
    p[0] = p[1]

def p_Var_Array(p):
    "Var : '[' Lista ']'"
    print("Array",p[2]) 
    if not p[2]:
        p[2] = "[]"
    p[0] = f"{p[2]}"

def p_Var_Dict(p):
    "Var : '{' Lista '}'"
    strRes = ""
    for elem in p[2]:
        lista = elem.split(':')
        key = lista[0]
        value = lista[1]
        strRes += f"\t{key} : {value},\n"
    p[0] = "{\n" + strRes + "}\n"

def p_TypeDeclaration_literals(p):
    "TypeDeclaration : LITERALS"
    p[0] = p[1]

def p_TypeDeclaration_ignore(p):
    "TypeDeclaration : IGNORE"
    p[0] = p[1]

def p_TypeDeclaration_tokens(p):
    "TypeDeclaration : TOKENS"
    p[0] = p[1]

def p_TypeDeclaration_precedence(p):
    "TypeDeclaration : PRECEDENCE"
    p[0] = p[1]

def p_Attrib_list(p):
    "Attrib : '[' Lista ']'"
    p[0] = p[2]

def p_Attrib_tuple(p):
    "Attrib : '(' Lista ')'"
    p[0] = p[2]

def p_Attrib_simple(p):
    "Attrib :  allQuotes"
    p[0] = p[1]

def p_Final(p):
    "Final : ','"

def p_Final_empty(p):
    "Final : "

def p_Lista_empty(p):
    "Lista :"
    p[0] = ""

def p_Lista(p):
    "Lista : Elems Final"
    p[0] = p[1]

def p_Elems_list (p):
    "Elems : Elems ',' Elem"
    p[0] = p[1] + [p[3]] 

def p_Elems_single(p):
    "Elems : Elem"
    p[0] = [p[1]]

def p_Elem(p):
    "Elem : str ElemFactor"
    p[0] = p[1] + p[2]

def p_Elem_Tuple(p):
    "Elem : '(' Tuple ')'"
    p[0] = f"({p[2]})"
    
def p_Elem_int(p):
    "Elem : int"
    p[0] = p[1]

def p_elem_float(p):
    "Elem : float"
    p[0] = p[1]

def p_ElemFactor_dict(p):
    "ElemFactor : ':' Var"
    p[0] = f":{p[2]}"

def p_ElemFactor_empty(p):
    "ElemFactor : "
    p[0] = ""

def p_Tuple_list(p):
    "Tuple : Tuple ',' Elem"
    p[0] = f"{p[1]},{p[3]}"

def p_Tuple_single(p):
    "Tuple : Elem"
    p[0] = p[1]

def p_Rules_list(p):
    "Rules : Rules Rule"

def p_Rules_empty(p):
    "Rules : Rule"

def p_Rule(p):
    "Rule : str ':' allQuotes allBraces"
    if p[1] not in p.parser.current[0]:
         p.parser.current[0][p[1]] = []
    p.parser.current[0][p[1]] += [{"rule": p[3], "code":p[4]}]



def p_error(token):
    if token is not None:
        print ("Line %s, illegal token %s | %s" % (token.lineno, token.value,token))
    else:
        print('Unexpected end of input')


def checkCast(statements,name):
    strRes =""
    types=["float","int"] # possible types to cast 
    # split into each statement
    lista = splitStatements(statements)
    for elem in lista:
        lRes = re.findall("(\w.+?)\((.+?)\)",elem) # check if is function
        if lRes:
            for res in lRes:
                #case for cast
                if res[0] in types: strRes += f"\t{res[1]} = {res[0]}({res[1]})\n"
                else: strRes += f"\t{elem}\n"
        else:
            # case for reserved
            if (elem == "#reserved") : strRes +=f"\t{lexVar}.type = reserved.get({lexVar}.value,'{name}')\n"   
            else: strRes += f"\t{elem}\n"
    return strRes


def lexFunction(name,function):
    strRes = ""
    elem= function[0]
    strRes += f"def t_{name}({lexVar}):\n"
    rule = elem['rule']
    rule = re.sub("\\''",'\"',rule)
    strRes += f"\tr{rule}\n"
    code = elem['code']
    code = code[1:-1] # remove braces
    if code != "":
        code = checkCast(code,name)
        strRes+= f"{code}"
    strRes += f"\treturn {lexVar}\n\n"
    return strRes


def findVarLex(rules):
    lista = ["value","type","lineno","lexpos","lexer"]
    elem = ".".join(map(str,rules))
    l = re.findall("(\w)\.(\w+)",elem)
    l = [x[0] for x in l if x[1] in lista]
    global lexVar
    if l:
        lexVar = max(set(l), key=l.count)

def buildLex(dict,dictVar):
    str = ""
    str += "import ply.lex as lex\n\n" 
    listTokens = dict['tokens']
    listTokens = [elem.replace("'","") for elem in listTokens] # remove single quotes from each token
    findVarLex(dict.values())
    str += buildVar(dictVar)
    lista = ["ignore","literals","tokens"]
    for key,elem in dict.items():
        if key not in lista:
            if key not in listTokens and key != "error":
                raiseError("Lex",f"'{key}' not in Tokens")
            str += lexFunction(key,elem)
            if key in listTokens:
                listTokens.remove(key)
        else:
            if key == "ignore":
                key = "t_ignore"
            if type(elem) is list:
                elem = arrayToString(elem)
            str += f"{key} = {elem}"
            if key == "tokens" and "reserved" in dictVar:
                str += "+ list(reserved.values())"
            str += "\n"
    if listTokens:
        raiseError("Lex",f"these tokens {arrayToString(listTokens)} are not defined")
    str += "lex.lex()\n"
    return str

    
def buildCodeStatements(statements):
    strRes =""
    # split into each statement
    lista = splitStatements(statements)
    for elem in lista:
        strRes += f"\t{elem}\n"
    return strRes


# find which variable is used for yacc rules
def findVarYacc(lista):
    elem = ".".join(map(str,lista))
    l = re.findall("(\w)\[\d\]",elem)
    global grammarVar
    if l:
        grammarVar = max(set(l), key=l.count)

def buildGrammarRules(name,ruleList):
    strRes = ""
    for count, dict in enumerate(ruleList):
        strRes += f"def p_{name}_{count}({grammarVar}):\n"
        rule = dict['rule']
        rule = rule[1:-1] # remove quotes
        strRes += f"\t\"{name} : {rule}\"\n"
        code = dict['code']
        code = code[1:-1].strip() # remove braces and spaces in beg
        code = buildCodeStatements(code)
        strRes += f"{code}\n"
        count +=1
    return strRes


def buildYacc(grammar, dictVar):
    strRes = doImportYacc()
    strRes += buildVar(dictVar)
    findVarYacc(grammar.values())
    for key,elem in grammar.items():
        if key == "precedence":
            if type(elem) is list:
                elem = arrayToString(elem)
            strRes += f"{key} = {elem}\n\n"
        else:
            strRes += buildGrammarRules(key,elem)
    return strRes


def doImportYacc():
    resStr = ""
    l = None
    if  parser.noConv != "":
        l = re.search("(.*=)?(\w+)\.yacc\(\)",parser.noConv)
    if l is not None:
        resStr += f"import ply.yacc as {l[2]}\n"
    else:
        resStr += "from ply.yacc import *\n"
    resStr += f"from {importNameLex} import tokens, literals\n\n"
    return resStr



# Build the parser
parser = yacc.yacc()
parser.yacc=({},{})
parser.lex=({},{})
parser.current = []
parser.noConv = ""

import sys
if len(sys.argv)!= 2:
    print("Erro: Nº de argumentos inválidos\nÉ necessário um ficheiro como argumento")
    exit()
filename = sys.argv[1]
f = open(filename)
program = f.read()
codigo = parser.parse(program)

grammarVar = "p"
lexVar = "t"

# Build Lex
filenameLex = filename.split('.')[0] + "_lex.py"

lexStr =""
try:
    lexStr = buildLex(parser.lex[0],parser.lex[1])
except Exception as error:
    print(error)
    exit()

# Build Yacc
filenameYacc = filename.split('.')[0] + "_yacc.py"
importNameLex = filenameLex.split('.')[0]

yaccStr = ""
yaccStr += buildYacc(parser.yacc[0],parser.yacc[1])
yaccStr += parser.noConv

writeToFile(filenameLex,lexStr)
writeToFile(filenameYacc,yaccStr)

