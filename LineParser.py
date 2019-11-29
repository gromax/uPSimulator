import re
from expressionParser import *

class LineParser: # Définition classe
    """Classe
    """

    def __init__(self, originalLine, lineNumber): # Constructeur
        self.originalLine = originalLine
        self.cleanLine = self.suppCommentsAndEndSpaces(self.originalLine)
        self.indent = self.countIndent(self.cleanLine)
        self.lineNumber = lineNumber

        self.emptyLine = cleanLine == ""

        if len(cleanLine)>0 :
            self.analyse = self.epurer(cleanLine)
            self.instruc = self.parse(self.analyse)
        else:
            self.analyse = False
            self.instruc = False

    def suppCommentsAndEndSpaces(self, line):
        return re.sub("\s*(\#.*)?$","",line) # suppression d'espce final avec éventuellement les commentaires

    def countIndent(self, line):
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


