'''
objet contenant une variable mémoire
'''

class Variable:
    def __init__(self, nom, value = 0):
        self.__nom = nom
        self.__value = value

    def getName(self):
        return self.__nom

    def clone(self):
    	return Variable(self.__nom)

    def __str__(self):
        return "@"+self.__nom

    def getBinary(self, wordSize):
        '''
        Retourne chaîne de caractère représentant le code CA2 de self.__value
        '''
        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        return format(valueToCode, '0'+str(wordSize)+'b')
