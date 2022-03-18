
# Estratégia

## CSV 

### Primeira estratégia (Ficheiro CSV normais)

Primeiramente começamos por converter ficheiros CSV normais, sem nenhum dos requisitos adicionais

Para isso a nossa estratégia foi:

Com recurso ao lex, definimos como tokens:
- SEP (o separador ',')
- TEXT (tudo o que seja valor)
- NEWLINE (para a mudança de linha)

As expressões regulares usadas para estes tokens foram:

-  SEP 
    - `r','`
    - dá match apenas ao caratér ','

- TEXT
    - `r'(?![ \t]+$)[\w \t]+'`
    - dá match a tudo o que seja letras,digitos,_,espaço e tab, mas que não contenha apenas espaços, ou seja, tudo o que estiver entre vírgulas

- NEWLINE
    -`r'\n+'
    - dá match ao caráter '\n', uma ou mais vezes, caso haja linhas vazias, para serem ignoradas


Já temos todos os tokens necessários para ler o csv.
Mas ainda precisamos de diferenciar os headers(1ªlinha), dos restantes valores.

Para isso, vamos usar um estado do lexer.

```py
    ("header","exclusive")
```

Este estado vai servir para diferenciar o tratamento do header com os restantes valores.


O lexer vai ter três variáveis nossas:
    - header - para guardar a informação do header
    - line - para guardar a informação da linha atual
    - values - para guardar a informação de todas as linhas

Vamos dizer ao lexer para começar no estado header.

Assim para a primeira linha, quando há uma match para o token de TEXT, iremos adicionar o valor do match para a lista de headers.

Quando chega ao fim da linha, ou seja, quando há match no token NEWLINE, já temos a nossa lista dos headres completa, iremos passar para o estado "INITIAL", o estado default para o resto das linhas.


Agora, para cada match do token TEXT, iremos adicionar para a lista "line".

E quando chegamos ao fim dessa linha, adicionamos a lista "line" à lista "values", e inicializamos a lista "line" para uma lista vazia.


Assim quando o lexer chega ao fim, temos duas listas:

- a lista "headers", que contém o nome de todos os headers

- a lista "values", que guarda uma lista dos valores para cada linha


Agora precisamos de construir o dicionário.

Para isso iremos percorrer a lista dos values, para tratar uma linha de cada vez.

Agora que temos a linha, iremos percorrer a linha juntamente com os headers, e associar o header ao seu valor.

Repete-se o processo para todas as linhas e temos o nosso dicionário completo.

Agora é só preciso converter para json.

Para isso, fazemos uso do módulo json

```py
json.dumps(listDict, indent=4,ensure_ascii=False)
```

indent é usado para o nr de espaços usados para a identação do ficheiro json

ensure_ascci é usado para permitir carateres que não fazem parte do asccii como por exemplo carateres com acento

### Adição da lista