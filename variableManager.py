class VariableManager:
    def __init__(self): # Constructeur
        self.__listVariables = []
        self.__listVariablesNames = []
        self.__listLitterals = []

    def addVariable(self, variableObject):
        '''
        variableObject = variable sous la forme d'un objet de type Variable
        '''
        assert isinstance(variableObject, Variable)
        name = variableObject.getName()
        if not name in self.__listVariablesNames:
            self.__listVariables.append(variableObject)
            self.__listVariablesNames.append(name)

    def addVariableByName(self, variableName):
        '''
        variableName = chaîne de caractères, nom de variable
        Sortie = objet variable créé ou récupéré dans la liste
        '''
        variableObjectFound = self.getVariableByName(variableName)
        if variableObjectFound != None:
            return variableObjectFound
        variableObject = Variable(variableName)
        self.__listVariables.append(variableObject)
        self.__listVariablesNames.append(variableName)
        return variableObject

    def addLitteralByValue(self, value):
        assert isinstance(value, int)
        if not value in self.__listLitterals:
            self.__listLitterals.append(value)

    def getVariableByName(self, variableName):
        '''
        variableName = chaîne de caractères, nom de variable
        Sortie = objet variable trouvé ou None
        '''
        if not variableName in self.__listVariablesNames:
            return None
        index = self.__listVariablesNames.index(variableName)
        variableObject = self.__listVariables[index]
        return variableObject

class Variable:
    def __init__(self, nom):
        self.__nom = nom

    def getName(self):
        return self.__nom

    def __str__(self):
        return self.__nom

