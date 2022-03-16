
import ply.lex as lex

tokens = ["SEP","TEXT"]




def t_SEP(t):
    r','

def t_TEXT(t):
    r'\w+'
    print(t.value)


def t_error(t):
    print("Error")

lexer = lex.lex()
lexer.comment= False

f = open("texto.txt","r")

texto = f.read()

lexer.input(texto)


for tok in lexer:
    print(tok)


f.close()
