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

    def getValue(self):
        return self.__value

    def __str__(self):
        return "#"+str(self.__value)

    def isLitteral(self):
        return True
