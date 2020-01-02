from variable import Variable

class VariableManager:
    def __init__(self): # Constructeur
        self.__listVariables = []
        self.__listVariablesNames = []
        self.__listTempMemory = []

    def getMemoryIndex(self, variable, baseIndex):
        if variable in self.__listVariables:
            index = self.__listVariables.index(variable)
            return baseIndex + index
        if variable in self.__listTempMemory:
            index = self.__listTempMemory.index(variable)
            return baseIndex + len(self.__listVariables) + index
        return baseIndex

    def addVariable(self, variableObject):
        '''
        variableObject = variable sous la forme d'un objet de type Variable
        '''
        assert isinstance(variableObject, Variable)
        name = variableObject.getName()
        if not name in self.__listVariablesNames:
            self.__listVariables.append(variableObject)
            self.__listVariablesNames.append(name)

    def addTempMemory(self, index):
        '''
        index = int
        '''
        assert index >= 0
        while index >= len(self.__listTempMemory):
            newMemIndex = len(self.__listTempMemory)
            newMem = Variable("_m"+str(newMemIndex))
            self.__listTempMemory.append(newMem)
        return self.__listTempMemory[index]

    def getTempMemory(self, index):
        '''
        index = int
        '''
        assert index >= 0
        if index <len(self.__listTempMemory):
            return self.__listTempMemory[index]
        return self.addTempMemory(index)

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

    def getLitteralByValue(self, value):
        '''
        value = entier
        Sortie = objet litteral trouvé ou None
        '''
        if not value in self.__listLitteralsValues:
            return None
        index = self.__listLitteralsValues.index(value)
        litteralObject = self.__listLitterals[index]
        return litteralObject

    def getVariableForAsm(self):
        variables = [v for v in self.__listVariables]
        mem = [m for m in self.__listTempMemory]
        return variables + mem

