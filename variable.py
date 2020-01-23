'''
objet contenant une variable mémoire
'''

from errors import *

class Variable:
    def __init__(self, nom:str, value:int = 0):
        self.__nom = nom
        self.__value = value

    def getName(self) -> str:
        return self.__nom

    def clone(self) -> 'Variable':
        return Variable(self.__nom)

    def __str__(self) -> 'str':
        return "@"+self.__nom

    def getBinary(self, wordSize:int) -> 'str':
        '''
        Retourne chaîne de caractère représentant le code CA2 de self.__value
        '''
        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize or self.__value > 0 and outStr[1] == '1':
            raise CompilationError(f"{self} : Variable de valeur trop grande !")
        return outStr

    def getValue(self) -> int:
        return self.__value
