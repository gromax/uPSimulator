class VariableManager:
    def __init__(self): # Constructeur
        self.__listVariables = []
        self.__listVariablesNames = []
        self.__listLitteralsValues = []
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
