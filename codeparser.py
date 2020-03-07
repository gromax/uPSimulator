"""
.. module:: codeparser
   :synopsis: gestion du parse de l'ensemble du programme d'origine
"""

from typing import List, Optional
from lineparser import LineParser, Caracteristiques
from structuresnodes import *

class CodeParser: # Définition classe
    """Classe CodeParser
    Parse le contenu d'un fichier passé en paramètre au constructeur
    Une méthode public parseCode qui construit une liste d'objets LineParser avec organisation des enfants selon indentation
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
            self.parseCode(code.split("\n"))
        else:
            raise ParseError("Il faut donner 'filename' ou 'code'")

    def __parseFile(self, filename:str) -> None:
        # Lecture de toutes les lignes du fichier
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        self.parseCode(lines)
        return

    def parseCode(self, lignesCode:List[str]) -> None:
        # On boucle sur les lignes de code
        for num, line in enumerate(lignesCode):
            objLine = LineParser(line, num+1)
            caract = objLine.getCaracs()
            # Traitement ligne non vide
            if not caract['emptyLine'] :
                # Ajout des informations parsées dans le listing
                self.__listingCode.append(caract)

        self.__manageElif()
        self.__blocControl()
        self.__buildFinalNodeList()
        self.__structureList()
        return

    def __manageElif(self) -> bool:
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

    def __blocControl(self) -> None:
        # Contrôle des blocs et de l'indentation
        for indice in range(len(self.__listingCode)):
            if self.__listingCode[indice]['type'] in ("if", "elif", "else", "while"):
                # cas dernière ligne de code : on attend une instruction
                if indice+1 == len(self.__listingCode):
                    raise ParseError(f"Il manque une instruction en fin de programme après la ligne n°{self.__listingCode[indice]['lineNumber']} - bloc <{self.__listingCode[indice]['type']}>")
                # cas ligne instruction suivante doit avoir une indentation supplémentaire
                if self.__listingCode[indice+1]['indentation'] != self.__listingCode[indice]['indentation'] + 4:
                    raise ParseError(f"Problème d'indentation de l'instruction après la ligne n°{self.__listingCode[indice]['lineNumber']} - bloc <{self.__listingCode[indice]['type']}>")

        # Contrôle de if associé au else - Parcours de liste en sens inverse
        for line in reversed(self.__listingCode):
            if line['type'] == 'else':
                startIndice = self.__listingCode.index(line)
                startIndentation = line['indentation']
                nextIndice = startIndice - 1
                while nextIndice >= 0 and self.__listingCode[nextIndice]['indentation'] > startIndentation:
                    nextIndice -= 1
                if nextIndice == -1 or self.__listingCode[nextIndice]['type'] != 'if':
                    raise ParseError(f"Détection d'un <else> en ligne n°{self.__listingCode[startIndice]['lineNumber']} sans <if> associé")

    def __buildFinalNodeList(self) -> bool:
        #Construction de la liste d'objets StructureNode
        # print("")
        # new liste ! et revoir __structureList() ??

        # copie locale inversée de __listingCode
        localeListingCode = self.__listingCode[::-1]
        # liste des profondeurs
        listReverseProf = [localeListingCode[index]["indentation"] for index in range(len(localeListingCode))]
        # print(listReverseProf)
        # On commence par l'indentation maximale
        if len(listReverseProf) > 0:
            maximun = max(listReverseProf)
        else:
            maximun = -1
        flagElse = False
        # tant que l'on a un maximum > 0 il faut regrouper
        while maximun >= 0:
            indexMaximun = listReverseProf.index(maximun)
            # print(f"While Principal >> maximun {maximun} > indexMaximun {indexMaximun}")
            while listReverseProf[indexMaximun] == maximun :
                # Parcourir toutes les lignes suivantes ayant la même indentation
                blockInstruction:List[StructureNode] = []
                ligneCourante = indexMaximun
                # print(f"While Secondaire >> ligneCourante {ligneCourante} > listReverseProf[ligneCourante] {listReverseProf[ligneCourante]}")
                while (len(listReverseProf) > 0 and listReverseProf[ligneCourante] == maximun):
                    nodeInstruction:Optional[StructureNode] = None
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


    def __structureList(self) -> bool:
        #Parcours du listing pour ranger les enfants
        listProfondeur = [self.__listingCode[index]["indentation"] for index in range(len(self.__listingCode))]
        if len(listProfondeur) > 0:
            maximun = max(listProfondeur)
        else:
            maximun = -1
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


    def __recursiveStringifyLine(self, line:Caracteristiques, tab:int) -> str:
        strLine = " "*tab + ", ".join([f"{key}:{value}" for key, value in line.items() if key != "children"])
        if "children" in line:
            childrens = [self.__recursiveStringifyLine(child, tab+4) for child in line["children"]]
            strLine += "\n" + "\n".join(childrens)
        return strLine

    def __str__(self) -> str:
        strLines = [self.__recursiveStringifyLine(line,0) for line in self.__listingCode]
        return "\n".join(strLines)

    def getFinalStructuredList(self) -> List[StructureNode]:
        return self.__structuredListeNode


if __name__=="__main__":
    code = CodeParser(filename = "example.code")
    print("")
    print(str(code))
    print("")
    for item in code.getFinalStructuredList():
        print(item)

    print("")
    code = CodeParser(filename = "example2.code")
    for item in code.getFinalStructuredList():
        print(item)

    test_code = '''
x = 0
if x > 0:
    x = x - 1
elif x == 0 :
    x = x + 1
'''
    print("")
    code = CodeParser(code = test_code)
    for item in code.getFinalStructuredList():
        print(item)

        test_code = '''
x = 0
if x > 0:
    if x == 2:
        x = x - 1
elif x == 0 :
    x = x + 1
  print(x)
'''
    print("")
    code = CodeParser(code = test_code)
    for item in code.getFinalStructuredList():
        print(item)

    # test programme vide
    test_code = ''
    print("")
    code = CodeParser(code = test_code)
    for item in code.getFinalStructuredList():
        print(item)

