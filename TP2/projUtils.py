
import re 
def raiseError(fase,string):
    raise Exception(f"Execution aborted.\n{fase} Error: " + string)


def arrayToString(elem):
    return "[" + ",".join(map(str,elem)) + "]"


def writeToFile(filename,string):
    file = open(filename,"w")
    file.write(string)
    print(f"{filename} was sucessufuly generated")


def splitStatements (statements):
    lista = statements.split(',')
    for index,elem in enumerate(lista):
        if (elem.count('(') != elem.count(')')) or (elem.count('"')%2 != 0) or (elem.count('{') != elem.count('}')):
            lista[index+1] = lista[index] + ',' + lista[index +1]
            lista.remove(elem)
    return lista

def buildVar(dict):
    strRes = ""
    for key,value in dict.items():
        if value == "":
            #case for comment
            strRes += f"{key}\n"
        else:
            strRes += f"{key} = {value}\n"
    return strRes

