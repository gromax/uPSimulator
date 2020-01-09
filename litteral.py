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

    def getBinary(self, wordSize):
        if self.__value < 0:
            valuToCode = (~self.__value + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        return format(valueToCode, '0'+str(wordSize)+'b')

    def isBetween(self, minValue, maxValue):
        return minValue <= self.__value <= maxValue

    def __str__(self):
        return "#"+str(self.__value)
