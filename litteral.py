'''
Objet contenant un littéral
'''

class Litteral:
    def __init__(self, value, big=False):
        '''
        value = int ou None
        Si None, signifie que la valeur est mise au max
        ce qui arrive quand on fait pointer vers la ligne suivante
        big = True si au moment de la compilation on a décidé coder le littéral sur une pleine ligne
        '''
        assert value == None or isinstance(value,int)
        self.__value = value
        self.__big = (big == True)

    def clone(self):
        return Litteral(self.__value, self.__big)

    def negClone(self):
        if self.__value == None:
            return Litteral(None)
        return Litteral(-self.__value, self.__big)

    def setBig(self):
        '''
        met à True le marqueur indiquant que ce littéral devra occuper une ligne entière dans le codage final
        '''
        self.__big = True
        return self

    def isBig(self):
        return self.__big

    def getBinary(self, wordSize):
        '''
        Retourne la version binaire du littéral
        S'il est trop grand, retourne une chaîne de 1
        '''
        if self.__value == None:
            return "1"*wordSize
        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize:
            return "1"*wordSize
        return outStr

    def isBetween(self, minValue, maxValue):
        return self.__value == None or minValue <= self.__value <= maxValue

    def getValue(self):
        if self.__value == None:
            return 0
        return self.__value

    def __str__(self):
        if self.__value == None:
            return "#Next line"
        return "#"+str(self.__value)
