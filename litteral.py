'''
Objet contenant un littéral
'''

class Litteral:
    def __init__(self, value, big=False):
        '''
        value = int
        big = True si au moment de la compilation on a décidé coder le littéral sur une pleine ligne
        '''
        assert isinstance(value,int)
        self.__value = value
        self.__big = (big == True)

    def clone(self):
        return Litteral(self.__value, self.__big)

    def negClone(self):
        return Litteral(-self.__value, self.__big)

    def setBig(self):
        '''
        met à True le marqueur indiquant que ce littéral devra occuper une ligne entière dans le codage final
        '''
        self.__big = True
        return self

    def isBig(self, bitSize):
        '''
        Dans le cas d'un déplacement d'un grand littéral vers la ligne suivante,
        détermine si ce littéral logera dans l'espace prévu
        '''
        return
        return self.__big

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
            return "1".wordSize
        return self.getBinary(wordSize)

    def isBetween(self, minValue, maxValue):
        return minValue <= self.__value <= maxValue

    def getValue(self):
        return self.__value

    def __str__(self):
        return "#"+str(self.__value)
