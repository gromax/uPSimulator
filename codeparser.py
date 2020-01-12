from lineparser import *
from structuresnodes import *

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
        self.__structuredListeNode = [] # liste des objets Node construite à partir de __listingCode
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
            objLine = LineParser(line, num+1)
            caract = objLine.getCaracs()
            # Traitement ligne non vide
            if not caract['emptyLine'] :
                # Ajout des informations parsées dans le listing
                self.__listingCode.append(caract)
        lineIndentError = self.__verifyIndent()
        if lineIndentError != -1:
            raise ParseError(f"{lineIndentError} : Erreur d'indentation en ligne")
        lineElseError = self.__verifyElse()
        if lineElseError != -1:
            raise ParseError(f"{lineElseError} : else / elif n'est relié à aucun if.")
        self.__manageElif()
        self.__buildFinalNodeList()
        self.__structureList()
        return

    def __manageElif(self):
        # Gestion du cas Elif
        for line in self.__listingCode:
            if line['type'] == 'elif':
                startIndice = self.__listingCode.index(line)
                startIndentation = line['indentation']
                line['type'] = 'if'
                line['indentation'] += 4
                tmpLine = LineParser(' ' * startIndentation + 'else:', line['lineNumber'])
                caract = tmpLine.getCaracs()
                # on insère le else au niveau du elif devenu if
                self.__listingCode.insert(startIndice, caract)
                nextIndice = startIndice + 1
                while self.__listingCode[nextIndice + 1]['indentation'] > startIndentation:
                    self.__listingCode[nextIndice + 1]['indentation'] += 4
                    nextIndice += 1
                    if len(self.__listingCode) == nextIndice + 1: break
                # gestion du cas elif à nouveau après un cas elif traité précédemment

                if len(self.__listingCode) > nextIndice + 1 and self.__listingCode[nextIndice + 1]['type'] == 'elif':
                    startIndentation = self.__listingCode[nextIndice + 1]['indentation']
                    self.__listingCode[nextIndice + 1]['indentation'] += 4
                    nextIndice = nextIndice + 1
                    while self.__listingCode[nextIndice + 1]['indentation'] > startIndentation:
                        self.__listingCode[nextIndice + 1]['indentation'] += 4
                        nextIndice += 1
                        if len(self.__listingCode) == nextIndice + 1: break
                # gestion du cas else du elif
                if len(self.__listingCode) > nextIndice + 1 and self.__listingCode[nextIndice + 1]['type'] == 'else':
                    startIndentation = self.__listingCode[nextIndice + 1]['indentation']
                    self.__listingCode[nextIndice + 1]['indentation'] += 4
                    nextIndice = nextIndice + 1
                    while self.__listingCode[nextIndice + 1]['indentation'] > startIndentation:
                        self.__listingCode[nextIndice + 1]['indentation'] += 4
                        nextIndice += 1
                        if len(self.__listingCode) == nextIndice + 1: break
        return True

    def __verifyIndent(self):
        '''
        retourne le numéro de ligne d'une erreur d'indentation
        L'indentation est libre, pas forcément +4
        Elle ne peut augmenter qu'après if, elif, else, while
        Quand elle diminue, elle doit retomber à un niveau déjà rencontré antérieurement
        -1 s'il n'y en a pas
        '''
        indentedBlocks = ('if', 'elif', 'else', 'while')
        if len(self.__listingCode) == 0:
            # liste vide
            return -1
        # doit commencer à 0
        lines = [(line['indentation'], line['type'], line['lineNumber']) for line in self.__listingCode[1:]]
        if indents[0] != 0:
            return -1
        previousIndents = [0]
        previousNeedIndent = self.__listingCode[0]['type'] in indentedBlocks
        for currentIndent, currentType, currentLineNumber in lines:
            if currentIndent > previousIndents[-1]:
                if previousNeedIndent in indentedBlocks:
                    previousIndents.append(currentIndent)
                else:
                    return currentLineNumber
            elif previousNeddIndent and currentIndent <= prepreviousIndents[-1]:
                return currentLineNumber
            elif currentIndent < previousIndents[-1]:
                while previousIndents[-1] > currentIndent:
                    previousIndents.pop()
                if currentIndent != previousIndents[-1]:
                    return currentLineNumber
            previousNeedIndent = currentType in indentedBlocks
        # ne doit pas terminé par un item nécessitant indentation
        if previousNeddIndent:
            return lineNumber
        return -1

    def __verifyElse(self):
        '''
        vérifie si un else ou elif donné correspond bien à un if
        retourne la ligne de l'erreur s'il y en a une
        -1 si pas d'erreur
        '''
        if len(self.__listingCode) == 0:
            # liste vide
            return -1
        lines = [(line['indentation'], line['type'], line['lineNumber']) for line in self.__listingCode]
        previousIfIndents = []
        for currentIndent, currentType, currentLineNumber in lines:
            # fermeture de tout if d'indentation supérieure
            while len(peviousIfIndents) > 0 and previousIfIndents[-1] > currentIndent:
                previousIfIndents.pop()
            if currentType == "else" or currentType == "elif":
                # ce cas doit poursuivre un if ouvert au même niveau
                if len(previousIfIndents) == 0 or previousIfIndents[-1] != currentIndent:
                    return lineNumber
                if currentType == "else":
                    # referme le if
                    previousIfIndents.pop()
            else
                # si if ouvert au même niveau, il se referme
                if len(previousIfIndents) > 0 and previousIfIndents[-1] == currentIndent:
                    previousIfIndents.pop()
                if currentType == "if":
                    # on ouvre un nouveau if
                    previousIfIndents.push(currentIndent)
        return -1

    def __buildFinalNodeList(self):
        #Construction de la liste d'objets StructureNode
        # print("")
        # new liste ! et revoir __structureList() ??

        # copie locale inversée de __listingCode
        localeListingCode = self.__listingCode[::-1]
        # liste des profondeurs
        listReverseProf = [localeListingCode[index]["indentation"] for index in range(len(localeListingCode))]
        # print(listReverseProf)
        # On commence par l'indentation maximale
        maximun = max(listReverseProf)
        flagElse = False
        # tant que l'on a un maximum > 0 il faut regrouper
        while maximun >= 0:
            indexMaximun = listReverseProf.index(maximun)
            # print(f"While Principal >> maximun {maximun} > indexMaximun {indexMaximun}")
            while listReverseProf[indexMaximun] == maximun :
                # Parcourir toutes les lignes suivantes ayant la même indentation
                blockInstruction = []
                ligneCourante = indexMaximun
                # print(f"While Secondaire >> ligneCourante {ligneCourante} > listReverseProf[ligneCourante] {listReverseProf[ligneCourante]}")
                while (len(listReverseProf) > 0 and listReverseProf[ligneCourante] == maximun):
                    nodeInstruction = ""
                    lineInstruction = localeListingCode.pop(ligneCourante)
                    listReverseProf.pop(ligneCourante)
                    # print(f"While Interne >> lineInstruction")
                    # print(listReverseProf)
                    # print(lineInstruction)
                    # On détermine la StructureNode associée à la ligne instruction
                    if lineInstruction['type'] == 'affectation':
                        nodeInstruction = AffectationNode(lineInstruction['lineNumber'],lineInstruction['variable'],lineInstruction['expression'])
                    if lineInstruction['type'] == 'input':
                        nodeInstruction = InputNode(lineInstruction['lineNumber'],lineInstruction['variable'])
                    if lineInstruction['type'] == 'print':
                        nodeInstruction = PrintNode(lineInstruction['lineNumber'],lineInstruction['expression'])
                    if lineInstruction['type'] == 'else':
                        flagElse = True
                        blockElseListInstruction = lineInstruction['children']
                        blockElseLine = lineInstruction['lineNumber']
                    if lineInstruction['type'] == 'if':
                        blockIfListInstruction = lineInstruction['children']
                        blockIfLine = lineInstruction['lineNumber']
                        if flagElse:
                            nodeInstruction = IfElseNode(blockIfLine,lineInstruction['condition'],blockIfListInstruction,blockElseLine,blockElseListInstruction)
                        else:
                            nodeInstruction = IfNode(blockIfLine,lineInstruction['condition'],blockIfListInstruction)
                        flagElse = False
                    if lineInstruction['type'] == 'while':
                        blockWhileListInstruction = lineInstruction['children']
                        blockWhileLine = lineInstruction['lineNumber']
                        nodeInstruction = WhileNode(blockWhileLine,lineInstruction['condition'],blockWhileListInstruction)

                    # Listing des instructions dans un même bloc - Pour le else nodeInstruction n'est pas affecté
                    if isinstance(nodeInstruction,StructureNode):
                        blockInstruction.insert(0,nodeInstruction)
                    # print(blockInstruction)

                    # print(f"{len(listReverseProf)} {indexMaximun}")

                    # On sort si on a vidé la liste (cas sortie du niveau 0 d'indentation)
                    if len(listReverseProf) == 0:
                        break

                # Cas du niveau indentation 0 -> On alimente __structuredListeNode
                if indexMaximun == 0:
                    # print("indexMaximun == 0 >> On alimente __structuredListeNode")
                    self.__structuredListeNode = blockInstruction

                # On sort si on a vidé la liste (cas sortie du niveau 0 d'indentation)
                if len(listReverseProf) == 0:
                    break

                # cas d'un bloc instruction à associer au children du container
                # print(f"Fin bloc instruction --> Affectation à children : {ligneCourante}")
                localeListingCode[ligneCourante]['children'] = []
                localeListingCode[ligneCourante]['children'] = blockInstruction

            # On sort si on a vidé la liste (cas sortie du niveau 0 d'indentation)
            if len(listReverseProf) == 0:
                break

            # Nouveau maximum d'indentation à trairer
            maximun = max(listReverseProf)

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
                if len(listProfondeur) == indexMaximun:
                    break
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

    def getFinalStructuredList(self):
        return self.__structuredListeNode


if __name__=="__main__":
    code = CodeParser(filename = "example.code")
    print("")
    print(str(code))
    print("")
    print(code.getFinalStructuredList())

    from compilemanager import *
    from processorengine import ProcessorEngine
    engine = ProcessorEngine()
    cm = CompilationManager(engine, code.getFinalStructuredList())
    listCompiled = cm.getLinearNodeList()
    for item in listCompiled:
        print(item)
    print()
    print(cm.getAsm())
    print()
    print(cm.getAsm().getBinary())
