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

    def isBetween(self, minValue, maxValue):
        return minValue <= self.__value <= maxValue

    def getValue(self):
        return self.__value

    def __str__(self):
        return "#"+str(self.__value)
