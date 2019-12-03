class VariableManager:
    def __init__(self): # Constructeur
        self.__list = []
        self.__listNames = []

    def addVariable(self, variableObject):
        '''
        variableObject = variable sous la forme d'un objet de type Variable
        '''
        assert isinstance(variableObject, Variable)
        name = variableObject.getName()
        if not name in self.__listNames:
            self.__list.append(variableObject)
            self.__listNames.append(name)

    def addVariableByName(self, variableName):
        '''
        variableName = chaîne de caractères, nom de variable
        Sortie = objet variable créé ou récupéré dans la liste
        '''
        variableObjectFound = self.getVariableByName(variableName)
        if variableObjectFound != None:
            return variableObjectFound
        variableObject = Variable(variableName)
        self.__list.append(variableObject)
        self.__listNames.append(variableName)
        return variableObject

    def getVariableByName(self, variableName):
        '''
        variableName = chaîne de caractères, nom de variable
        Sortie = objet variable trouvé ou None
        '''
        if not variableName in self.__listNames:
            return None
        index = self.__listNames.index(variableName)
        variableObject = self.__listNames[index]
        return variableObject

class Variable:
    def __init__(self, nom):
        self.__nom = nom

    def getName(self):
        return self.__nom

    def __str__(self):
        return self.__nom


