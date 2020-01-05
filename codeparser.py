from lineparser import *

class CodeParser: # Définition classe
    """Classe CodeParser
    Parse le contenu d'un fichier passé en paramètre au constructeur
    Une méthode public parseCode qui construit une liste d'objets LineParser avec organisation des enfants selon indentation
    La méthode getFinalParse retourne cette liste d'objets LineParser
    TODO - une méthode de contrôle de cohérence du code
    ATTENTION - pas de gestion particulière du if, elif, else -> pas de tuple pour le noeud if et else --> voir structureelements
    """

    def __init__(self, **options): # Constructeur
        '''
        options doit contenir l'un des attributs :
        - filename : nom de fichier contenant le code
        - code : chaîne de caractère contenant le code
        '''
        self.__listingCode = [] # liste des objets LineParser de chaque ligne du code parsé
        if "filename" in options:
            filename = options["filename"]
            self.__parseFile(filename)
        elif "code" in options:
            code = options["code"]
            self.parseCode(code)
        else:
            raise ParseError("Il faut doner 'filename' ou 'code'")

    def __parseFile(self, filename):
        # Lecture de toutes les lignes du fichier
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        self.parseCode(lines)
        return

    def parseCode(self, lignesCode):
        # On boucle sur les lignes de code
        for num, line in enumerate(lignesCode):
            objDictLine = {}
            objLine = LineParser(line, num)
            caract = objLine.getCaracs()
            # Traitement ligne non vide
            if not caract['emptyLine'] :
                # Ajout des informations parsées dans le listing
                self.__listingCode.append(caract)
        self.__structureList()
        return

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

    def __recursiveStringifyLine(self, line, tab):
        strLine = " "*tab + ", ".join([f"{key}:{value}" for key, value in line.items() if key != "children"])
        if "children" in line:
            childrens = [self.__recursiveStringifyLine(child, tab+4) for child in line["children"]]
            strLine += "\n" + "\n".join(childrens)
        return strLine

    def __str__(self):
        strLines = [self.__recursiveStringifyLine(line,0) for line in self.__listingCode]
        return "\n".join(strLines)

    def getFinalParse(self):
        return self.__listingCode


if __name__=="__main__":
    code = CodeParser(filename = "example.code")
    print(str(code))
