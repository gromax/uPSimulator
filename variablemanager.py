class VariableManager:
    def __init__(self): # Constructeur
        self.__listVariables = []
        self.__listVariablesNames = []
        self.__listLitteralsValues = []
        self.__listLitterals = []
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


    def addLitteralByValue(self, value):
        '''
        value = entier
        Sortie = objet litteral créé ou récupéré dans la liste
        '''
        litteralObjectFound = self.getLitteralByValue(value)
        if litteralObjectFound != None:
            return litteralObjectFound
        self.__listLitteralsValues.append(value)
        litteralObject = Litteral(value)
        self.__listLitterals.append(litteralObject)
        return litteralObject

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



class Variable:
    def __init__(self, nom):
        self.__nom = nom

    def getName(self):
        return self.__nom

    def __str__(self):
        return "@"+self.__nom

    def isLitteral(self):
        return False

class Litteral:
    def __init__(self, value):
        assert isinstance(value,int)
        self.__value = value

    def getValue(self):
        return self.__value

    def __str__(self):
        return "#"+str(self.__value)

    def isLitteral(self):
        return True
