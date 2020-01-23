'''
Objet contenant un littéral
'''

class Litteral:
    def __init__(self, value):
        '''
        value = int
        '''
        assert isinstance(value,int)
        self.__value = value

    def clone(self):
        return Litteral(self.__value)

    def negClone(self):
        return Litteral(-self.__value)

    def isBig(self, bitSize):
        '''
        Dans le cas d'un déplacement d'un grand littéral vers la ligne suivante,
        détermine si ce littéral logera dans l'espace prévu
        '''
        return not self.isBetween(0,2**bitSize-2)

    def getBinary(self, wordSize):
        '''
        Retourne la version binaire du littéral
        S'il est trop grand, retourne une chaîne de 1
        '''
        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize:
            return "1"*wordSize
        return outStr

    def getBinaryForPos(self, wordSize):
        '''
        Retourne la version binaire du littéral
        S'il est trop grand ou négatif, retourne une chaîne de 1
        '''
        if self.__value < 0:
            return "1"*wordSize
        return self.getBinary(wordSize)

    def isBetween(self, minValue, maxValue):
        return minValue <= self.__value <= maxValue

    def getValue(self):
        return self.__value

    def __str__(self):
        return "#"+str(self.__value)
