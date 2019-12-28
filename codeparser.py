from lineparser import *

class CodeParser: # Définition classe
    """Classe CodeParser
    Parse le contenu d'un fichier passé en paramètre au constructeur
    Une méthode public parseCode qui construit une liste d'objets LineParser avec organisation des enfants selon indentation
    La méthode getFinalParse retourne cette liste d'objets LineParser
    TODO - une méthode de contrôle de cohérence du code
    ATTENTION - pas de gestion particulière du if, elif, else -> pas de tuple pour le noeud if et else --> voir structureelements
    """

    #Instanciation VariableManager
    variableManagerObject = VariableManager()

    def __init__(self, filename=None): # Constructeur
        self.__listingCode = [] # liste des objets LineParser de chaque ligne du code parsé
        if filename != None:
            self.__parseFile(filename)


    def __parseFile(self, filename):
        # Lecture de toutes les lignes du fichier
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        self.parseCode(lines)
        return True

    def parseCode(self, lignesCode):
        # On boucle sur les lignes de code
        for num, line in enumerate(lignesCode):
            objDictLine = {}
            print(line)
            objLine = LineParser(line,num,self.variableManagerObject)
            caract = objLine.getCaracs()
            # Traitement ligne non vide
            if not caract['emptyLine'] :
                # Ajout des informations parsées dans le listing
                self.__listingCode.append(caract)
        self.__structureList()
        return True

    def __structureList(self):
        #Parcours du listing pour ranger les enfants
        listProfondeur = [self.__listingCode[index]["indentation"] for index in range(len(self.__listingCode))]
        # print(listProfondeur)
        maximun = max(listProfondeur)
        while maximun > 0:
            indexMaximun = listProfondeur.index(maximun)
            self.__listingCode[indexMaximun - 1]['children'] = []
            while listProfondeur[indexMaximun] == maximun :
                self.__listingCode[indexMaximun - 1]['children'].append(self.__listingCode.pop(indexMaximun))
                listProfondeur.pop(indexMaximun)
            maximun = max(listProfondeur)
        return True

    def getFinalParse(self):
        return self.__listingCode


if __name__=="__main__":

    code = CodeParser("example.py")
    codeParsed = code.getFinalParse()

    for elem in codeParsed:
        print(elem)

    from structureelements import *
    c = Container()
    c.append(codeParsed)
    print()
    print(c)
    print()
    print("Version linéarisée :")
    print()
    lC = c.getLinearized()
    print(lC)
