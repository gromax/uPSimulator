"""
.. module:: modules.parser.code
:synopsis: gestion du parse de l'ensemble du programme d'origine
"""

from typing import List, Optional
import re

from modules.parser.lineparser import ParsedLine, ParsedLine_Elif, ParsedLine_If, ParsedLine_While, ParsedLine_Else, ParsedLine_Print, ParsedLine_Affectation, ParsedLine_Input
from modules.structuresnodes import StructureNode, WhileNode, IfElseNode, IfNode, TransfertNode
from modules.errors import ParseError

class CodeParser: # Définition classe
    """Classe CodeParser
    Parse le contenu d'un fichier passé en paramètre au constructeur
    Une méthode public parseCode qui construit une liste d'objets LineParser avec organisation des enfants selon indentation
    """

    @classmethod
    def parse(cls, **options) -> List[StructureNode]:
        """
        parse le contenu de l'entité fournie :
        options doit contenir l'un des attributs :
        - filename : nom de fichier contenant le code
        - code : chaîne de caractère contenant le code
        """
        if "filename" in options:
            filename = options["filename"]
            return cls._parseFile(filename)
        if "code" in options:
            code = options["code"]
            return cls._parseCode(code.split("\n"))
        raise ParseError("Il faut donner 'filename' ou 'code'")

    @classmethod
    def _parseFile(cls, filename:str) -> List[StructureNode]:
        """Ouverture d'un fichier avant parse

        :param filename: nom du fichier
        :type filename: str
        :return: liste de noeuds représentant le programme
        :rtype: List[StructureNode]
        """
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        return cls._parseCode(lines)

    @classmethod
    def _parseCode(cls, lignesCode:List[str]) -> List[StructureNode]:
        """Parse du programme donné sous forme d'une liste de lignes

        :param lignesCode: lignes du programme
        :type filename: List[str]
        :return: liste de noeuds représentant le programme
        :rtype: List[StructureNode]
        """

        listParsedLines: List[ParsedLine] = []
        for index, line in enumerate(lignesCode):
            objLine = cls._parseLine(line, index+1)
            # Traitement ligne non vide
            if not objLine.empty:
                # Ajout des informations parsées dans le listing
                listParsedLines.append(objLine)

        indentationErrorLineNumber = cls._verifyIndent(listParsedLines)
        if indentationErrorLineNumber >= 0:
            raise ParseError("Erreur d'indentation.", {"lineNumber": indentationErrorLineNumber})

        elseErrorLineNumber = cls._verifyElse(listParsedLines)
        if elseErrorLineNumber >= 0:
            raise ParseError("elif ou else n'est pas correctement lié à un if.", {"lineNumber": elseErrorLineNumber})

        groupedList = cls._groupBlocs(listParsedLines)
        return cls._convertParsedLinesToStructurNodes(groupedList)

    @classmethod
    def _verifyIndent(cls, listParsedLines:List[ParsedLine]) -> int:
        """
        vérifie le bon enchaînement des indentations

        :param listParsedLines: liste des lignes parsées
        :type listParsedLines: List[ParsedLine]
        :return: numéro de ligne d'une éventuelle erreur, -1 si pas d'erreur
        :rtype: int
        """

        if len(listParsedLines) == 0:
            # liste vide
            return -1
        firstLine = listParsedLines[0]
        previousIndents = [firstLine.indentation]
        for index in range(1,len(listParsedLines)):
            currentLine  = listParsedLines[index]
            previousLine = listParsedLines[index-1]
            if previousLine.needIndentation():
                # augmentation de l'indentation requise
                if currentLine.indentation > previousLine.indentation:
                    previousIndents.append(currentLine.indentation)
                    continue
                return currentLine.lineNumber
            if currentLine.indentation > previousLine.indentation:
                # augmentation imprévue de l'indentation
                return currentLine.lineNumber
            if currentLine.indentation < previousLine.indentation:
                # diminution de l'indentation
                # doit revenir à un niveau antérieur
                while len(previousIndents) > 0 and previousIndents[-1] > currentLine.indentation:
                    # dépile un niveau d'indentation
                    previousIndents.pop()
                if len(previousIndents) == 0 or previousIndents[-1] < currentLine.indentation:
                    # l'indentation courante est soit trop faible soit pas sur un niveau antérieur
                    return currentLine.lineNumber
        # ne doit pas terminé par un item nécessitant indentation
        lastLine = listParsedLines[-1]
        if lastLine.needIndentation():
            return lastLine.lineNumber
        return -1

    @classmethod
    def _verifyElse(cls, listParsedLines:List[ParsedLine]) -> int:
        """
        vérifie si un else ou elif donné correspond bien à un if

        :param listParsedLines: liste des lignes parsées
        :type listParsedLines: List[ParsedLine]
        :return: numéro de ligne d'une éventuelle erreur, -1 si pas d'erreur
        :rtype: int
        """
        if len(listParsedLines) == 0:
            # liste vide
            return -1
        # recherche un else ou elif
        for index in range(len(listParsedLines)):
            currentLine = listParsedLines[index]
            if isinstance(currentLine, (ParsedLine_Elif, ParsedLine_Else)):
                # Il faut remonter vers la ligne antérieure de même indentation
                # pour s'assurer que c'est un if ou elif
                precedent = index-1
                while precedent >= 0 and listParsedLines[precedent].indentation > currentLine.indentation:
                    precedent -= 1
                if precedent < 0:
                    # on n'a pas trouvé d'indentation antérieure valable
                    return currentLine.lineNumber
                precLine = listParsedLines[precedent]
                if not isinstance(precLine, (ParsedLine_If, ParsedLine_Elif)):
                    # l'antécédent à la même indentation n'est ni if ni elif donc erreur
                    return currentLine.lineNumber
        return -1

    @classmethod
    def _getIndexEndIndentation(cls, startIndex:int, listParsedLines:List[ParsedLine]) -> int:
        """
        en référence à l'indentation du premier élément, cherchel l'index pour lequel
        l'indentation passe en dessous de l'indentation à l'index startIndex

        :param startIndex: index du premier élément considéré
        :type startIndex: int
        :param listParsedLines: liste des lignes parsées
        :type listParsedLines: List[ParsedLine]
        :return: index du premier item dont l'indentaiton passe en dessous de l'indentation du premier élément ou longueur de la liste
        :rtype: int
        """
        if startIndex >= len(listParsedLines) - 1:
            return startIndex + 1
        firstLine = listParsedLines[startIndex]
        firstIndentation = firstLine.indentation
        for index in range(startIndex+1,len(listParsedLines)):
            line = listParsedLines[index]
            if line.indentation < firstIndentation:
                return index
        return len(listParsedLines)

    @classmethod
    def _groupBlocs(cls, listParsedLines:List[ParsedLine]) -> List[ParsedLine]:
        """
        regroupe les blocs en arborescence suivant l'indentation

        :param listParsedLines: liste des lignes parsées
        :type listParsedLines: List[ParsedLine]
        :return: liste avec les blocs regroupés
        :rtype: List[ParsedLine]
        """
        if len(listParsedLines) == 0:
            return []
        alreadyGrouped = [listParsedLines[0]]
        currentIndex = 1
        while currentIndex < len(listParsedLines):
            previousLine = alreadyGrouped[-1]
            currentLine = listParsedLines[currentIndex]
            if currentLine.indentation < previousLine.indentation:
                # ce bloc est terminé
                return alreadyGrouped
            if currentLine.indentation == previousLine.indentation:
                # même indentation, le bloc se poursuit
                currentIndex += 1
                alreadyGrouped.append(currentLine)
                continue
            # dernier cas : augmentation indentation
            # il faut collecter le bloc
            nextIndex = cls._getIndexEndIndentation(currentIndex, listParsedLines)
            subBloc = listParsedLines[currentIndex:nextIndex]
            subBlocGrouped = cls._groupBlocs(subBloc) # propagation récursive
            previousLine.addChildren(subBlocGrouped)
            currentIndex = nextIndex
        return cls._convertElifToElseIf(alreadyGrouped)

    @classmethod
    def _convertElifToElseIf(cls, listParsedLine:List[ParsedLine]):
        """
        coupe les elif en else contenant if

        :param listParsedLines: liste des lignes parsées
        :type listParsedLines: List[ParsedLine]
        :return: liste avec les elif séparés
        :rtype: List[ParsedLine]
        """
        reversedListParsedLines = listParsedLine[::-1]
        modifiedList:List[ParsedLine] = []
        pendindElse:Optional[ParsedLine_Else] = None
        for currentLine in reversedListParsedLines:
            if isinstance(currentLine, ParsedLine_Else):
                pendindElse = currentLine
            elif isinstance(currentLine, ParsedLine_Elif):
                newElse = currentLine.toElseIf()
                if not(pendindElse is None):
                    newElse.addChild(pendindElse)
                pendindElse = newElse
            elif isinstance(currentLine, ParsedLine_If): # après, attention héritage !
                if not(pendindElse is None):
                    modifiedList.append(pendindElse)
                    pendindElse = None
                modifiedList.append(currentLine)
            else:
                modifiedList.append(currentLine)
        return modifiedList[::-1]

    @classmethod
    def _convertParsedLinesToStructurNodes(cls, listParsedLine:List[ParsedLine]) -> List['StructureNode']:
        """Convertit une liste de ParsedLine en liste de StructureNode

        :param listParsedLine: liste des objets à convertir
        :type parsedLine: List[ParsedLine]
        :return: liste sous forme de StructureNode
        :rtype: List[StructureNode]
        """

        reversedListParsedLines = listParsedLine[::-1]
        outList:List[StructureNode] = []
        pendingElse:Optional[ParsedLine_Else] = None
        newNode: StructureNode
        children: List[StructureNode]
        elseChildren: List[StructureNode]
        for line in reversedListParsedLines:
            if isinstance(line, ParsedLine_Else):
                pendingElse = line
                continue
            elif isinstance(line, ParsedLine_While): # While avant If, Attention héritage !
                children = cls._convertParsedLinesToStructurNodes(line.children)
                newNode = WhileNode(line.lineNumber, line.condition, children)
            elif isinstance(line, ParsedLine_If) and not(pendingElse is None):
                children = cls._convertParsedLinesToStructurNodes(line.children)
                elseChildren = cls._convertParsedLinesToStructurNodes(pendingElse.children)
                newNode = IfElseNode(line.lineNumber, line.condition, children, pendingElse.lineNumber, elseChildren)
            elif isinstance(line, ParsedLine_If):
                children = cls._convertParsedLinesToStructurNodes(line.children)
                newNode = IfNode(line.lineNumber, line.condition, children)
            elif isinstance(line, ParsedLine_Print):
                newNode = TransfertNode(line.lineNumber, None, line.expression)
            elif isinstance(line, ParsedLine_Input):
                newNode = TransfertNode(line.lineNumber, line.variable, None)
            elif isinstance(line, ParsedLine_Affectation):
                newNode = TransfertNode(line.lineNumber, line.variable, line.expression)
            else:
                raise ParseError("Erreur imprévue.", {"lineNumber":line.lineNumber})
            outList.append(newNode)

        return outList[::-1]

    # méthodes concernant la gestion d'une ligne
    @classmethod
    def _parseLine(cls, originalLine:str, lineNumber:int) -> ParsedLine:
        """parse d'une ligne

        :param originalLine: ligne d'origine
        :type originalLine: str
        :param lineNumber: numéro de la ligne d'origine
        :type line Number: int
        :return: noeud de type LP
        :raises: ParseError si type de ligne pas reconnue
        """

        cleanLine   = cls._suppCommentsAndEndSpaces(originalLine)
        emptyLine   = (cleanLine == "")
        indentation = cls._countIndentation(originalLine)

        if emptyLine:
            return ParsedLine(lineNumber)

        classesToTry = (ParsedLine_If, ParsedLine_Elif, ParsedLine_While, ParsedLine_Else, ParsedLine_Print, ParsedLine_Input, ParsedLine_Affectation)
        # remarque : il faut tester input avant affectation car input() génère autrement une erreur
        # si interprété comme une expression
        for c in classesToTry:
            lineObject: Optional[ParsedLine] = c.tryNew(lineNumber, indentation, cleanLine)
            if not lineObject is None:
                return lineObject
        raise ParseError("Erreur de syntaxe : <{}>".format(cleanLine), {"lineNumber":lineNumber})

    @classmethod
    def _suppCommentsAndEndSpaces(cls, line:str) -> str:
        """
        :param line: ligne d'origine
        :type line: str
        :return: ligne sans les espaces initiaux et terminaux ainsi que les éventuels commentaires
        :rtype: str
        """
        return re.sub(r"\s*(\#.*)?$","",line).strip()

    @classmethod
    def _countIndentation(cls, line:str) -> int:
        """
        :param line: ligne dont il faut compter l'indentation
        :type line: str
        :return: nombre d'espaces d'indentation
        :rtype: int
        """
        line = re.sub(r"\s*(\#.*)?$","",line)
        return len(re.findall(r"^\s*",line)[0])







