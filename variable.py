'''
objet contenant une variable mémoire
'''

class Variable:
    def __init__(self, nom, value = 0):
        self.__nom = nom
        self.__value = int(value)

    def getName(self):
        return self.__nom

    def getValue(self):
        return self.__value

    def __str__(self):
        return "@"+self.__nom
