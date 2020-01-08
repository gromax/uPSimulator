'''
objet contenant une variable mémoire
'''

class Variable:
    def __init__(self, nom):
        self.__nom = nom

    def getName(self):
        return self.__nom

    def clone(self):
    	return Variable(self.__nom)

    def __str__(self):
        return "@"+self.__nom
