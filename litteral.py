'''
Objet contenant un littéral
'''

class Litteral:
    def __init__(self, value):
        '''
        value = int ou None
        Si None, signifie que la valeur est mise au max
        ce qui arrive quand on fait pointer vers la ligne suivante
        '''
        assert value == None or isinstance(value,int)
        self.__value = value

    def clone(self):
        return Litteral(self.__value)

    def negClone(self):
        if self.__value == None:
            return Litteral(None)
        return Litteral(-self.__value)

    def getBinary(self, wordSize):
        if self.__value == None:
            return "1"*wordSize
        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        return format(valueToCode, '0'+str(wordSize)+'b')

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
