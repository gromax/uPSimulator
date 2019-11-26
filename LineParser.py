import re
from expression import *
from expressionParser import *

class LineParser: # Définition classe
    """Classe 
    """
    def __init__(self, line): # Constructeur
        line = self.suppcomment(line)
        print(line)
        if len(line)>0 :            
            self.indent  = self.nbindent(line)
            self.analyse = self.epurer(line)
            self.instruc = self.parse(self.analyse)
        else:
            self.indent = 0
            self.analyse = False
            self.instruc = False

    def suppcomment(self, line):
        return re.sub("(^\#.*$)|(\s*\#[^\)]*)$","",line)

    def nbindent(self, line):
        return len(re.findall("^\s*",line)[0])

    def epurer(self, line):
        phrase = ""
        for mot in re.split("(?:(?=\s+)(\s+)|(?=\"+)(\"[^\"]+?\")|$)",line):
            if mot != None and len(mot) > 0 and not re.match("^\s*$",mot):
                if mot in ('and','or','not'):
                    phrase = phrase + ' ' + mot + ' '
                else:
                    phrase = phrase + mot
        return phrase

    def parse(self, line):
        motif = re.findall("(^\w+)(.*)",line)[0]       
        if (motif[0] in ['while','if']):
            if (motif[1][-1] == ':'): 
                return (motif[0], motif[1][:-1])
            else:
                return False
        elif (motif[0] in ['print']):
            return (motif[0], motif[1])
        else:
            return ('affectation', line)
            


txt = '    while ( A < B) : #comment'
#txt = 'if (A==B):' 
#txt = 'print("cou#cou")  #comment' 
#txt = 'A=" mon  texte "' 
#txt = 'A=A+1  #comment'

ligne = LineParser(txt)
print(ligne.indent)
print(ligne.analyse)
result = ligne.instruc
print(result, type(result))
print(result[1], type(result[1]))
result = ExpressionParser.buildTokensList(result[1])
print(result)

