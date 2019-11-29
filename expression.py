from expressionParser import *
from errors import *

class Expression:
    @staticmethod
    def strIsExpression(str):
        '''
        Entrée : chaine de caractères str
        Sortie: True si cela correspond à une expression
        '''
        return ExpressionParser.test(str)

    @classmethod
    def __recursive_getType(cls, node):
        '''
        Entrée : noeud de l'arbre de l'expression
        Sortie:
        - 'int' si le résultat est de type 'int',
        - 'bool' si le résultat est de type 'booléen',
        - None en cas d'erreur
        Parcours récursif de l'arbre
        '''
        if len(node) == 1:
            # variable ou littéral
            return 'int'
        if len(node) == 2:
            # opérateur unaire opérateur, opérande
            operator, child = node
            childType = cls.__recursive_getType(child)
            if childType == None or (operator=='~' and childType=='bool'):
                return None
            elif operator == "not":
                return 'bool'
            else:
                return 'int'
        # dernier cas, opérateur binaire
        operator, child1, child2 = node
        child1Type = cls.__recursive_getType(child1)
        child2Type = cls.__recursive_getType(child2)
        if child1Type != child2Type or child1Type == None or child2Type == None:
            return None
        elif child1Type == 'bool' and operator in "+-*/%&|":
            return None
        elif child1Type == 'bool' and operator in "and;or":
            return 'bool'
        elif child1Type == 'bool':
            # cas ==, <=...
            return None
        elif operator in "and;or":
            return None
        elif operator in "+-*/%&|":
            return 'int'
        else:
            # cas == <=...
            return 'bool'
    @classmethod
    def __recursive_toString(cls, node):
        '''
        Entrée : noeud de l'arbre de l'expression
        Sortie: chaine de caractère correspond au noeud
        Parcours récursif de l'arbre
        '''
        if len(node) == 1:
            # variable ou littéral
            value = node[0]
            return str(value)
        if len(node) == 2:
            # opérateur unaire opérateur, opérande
            operator, child = node
            strChild = cls.__recursive_toString(child)
            return operator+"("+strChild+")"
        # dernier cas, opérateur binaire
        operator, child1, child2 = node
        strChild1 = cls.__recursive_toString(child1)
        strChild2 = cls.__recursive_toString(child2)
        return "(" + strChild1 + " " + operator + " " + strChild2 + ")"

    @classmethod
    def __recursive_getVariablesNames(cls, node, variablesList):
        '''
        Entrée : noeud de l'arbre de l'expression, liste déjà constituée
        Sortie : La liste
        Parcours récursif de l'arbre
        '''
        if len(node) == 1:
            # variable ou littéral
            value = node[0]
            if isinstance(value, str) and value not in variablesList:
                variablesList.append(value)
            return variablesList
        if len(node) == 2:
            # opérateur unaire opérateur, opérande
            operator, child = node
            cls.__recursive_getVariablesNames(child, variablesList)
            return variablesList
        # dernier cas, opérateur binaire
        operator, child1, child2 = node
        cls.__recursive_getVariablesNames(child1, variablesList)
        cls.__recursive_getVariablesNames(child2, variablesList)
        return variablesList

    def __init__(self, tree):
        '''
        Entrée : Arbre représentant l'expression
        Chaque noeud est un tuple de nombre d'éléments :
        - 1: variable ou litteral,
        - 2: opérateur unaire = string opérateur, noeud opérande,
        - 3 opérateur binaire = string opérateur, noeud opérande 1, noeud opérande 2
        '''
        self.tree = tree

    def getType(self):
        '''
        Sortie :
        - 'int' si le résultat est de type 'int',
        - 'bool' si le résultat est de type 'booléen',
        - None en cas d'erreur
        Parcours récursif de l'arbre
        '''
        return self.__recursive_getType(self.tree)

    def __str__(self):
        '''
        Fonction de conversion de Expression en string
        '''
        return self.__recursive_toString(self.tree)

    def getVariablesNames(self):
        '''
        Sortie : liste des noms de variables utilisées dans l'expression
        '''
        variablesList = self.__recursive_getVariablesNames(self.tree, [])
        variablesList.sort()
        return variablesList

