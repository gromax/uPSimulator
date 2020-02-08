#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: compileexpressionmanager
   :synopsis: gestion de la compilation d'une expression
"""

from typing import Union, List, Tuple

from errors import *
from variable import Variable
from litteral import Litteral
from processorengine import ProcessorEngine
from assembleurcontainer import AssembleurContainer
from expressionnodes import ExpressionNode, BinaryNode, UnaryNode, ValueNode

class CompileExpressionManagerExp:
    __log:str = ""
    __registerStack:List[int]
    def __init__(self, engine:ProcessorEngine, asmManager:AssembleurContainer, lineNumber:int):
        """        Constructeur

        :param engine: modèle de processeur utilisé
        :type engine: ProcessorEngine
        :param asmManager: code assembleur
        :type asmManager: AssembleurContainer
        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        """

        self.__engine = engine
        self.__asmManager = asmManager
        self.__lineNumber = lineNumber
        self.__registersNumber = self.__engine.registersNumber()
        assert self.__registersNumber > 1
        self.resetMemory()

    ### private
    def __freeRegister(self) -> int:
        """Libère le dernier registre de la pile des registres.

        :return: le registre libéré
        :rtype: int
        :raises: CompilationError s'il n'y a aucun registre à libérer

        .. warning:: ne doit pas tomber sur une mémoire temporaire
        """
        if len(self.__registerStack) == 0:
            self.__log += "Erreur : plus de registre à libérer.\n"
            raise CompilationError("Aucun registre à libérer.")
        register = self.__registerStack.pop()
        assert register >= 0
        self.__availableRegisters.append(register)
        self.__log += f"Libération de r{register}\n"
        return register

    def __getTopStackRegister(self) -> int:
        """
        :return: numéro du registre au sommet de la pile, sans le libérer.
        :rtype: int
        :raises: CompilationError s'il n'y a pas d'opérande dans la pile
        .. note:: si le numéro est ``< 0``, provoque le dépilage d'un item de mémoire et retour du numéro de registre ayant accueilli le retour.
        """
        if len(self.__registerStack) == 0:
            raise CompilationError("Pas assez d'opérande dans la pile.")
        register = self.__registerStack[-1]
        if register < 0:
            self.__registerStack.pop()
            register = self.__moveMemoryToFreeRegister()
        return register

    def __swapStackRegister(self) -> None:
        """Intervertit les contenus des deux derniers étages de la pile des registres

        :raises: CompilationError s'il n'y a pas assez d'opérandes pour le swap
        """
        if len(self.__registerStack) < 2:
            raise CompilationError("Pas assez d'opérande dans la pile pour swap.")
        op1 = self.__registerStack[-1]
        op2 = self.__registerStack[-2]
        self.__registerStack[-1] = op2
        self.__registerStack[-2] = op1
        self.__log += f"Permutation registres (mémoires) {op1} et {op2}\n"

    def __availableRegisterExists(self) -> bool:
        """
        :return: vrai si un registre est disponible
        :rtype: bool
        """
        return len(self.__availableRegisters) > 0

    def __getAvailableRegister(self) -> int:
        """Retourne un registre disponible.

        :return: numéro du prochain registre disponible
        :rtype: int
        :raises: CompilationError si aucune registre n'est disponible
        """
        if len(self.__availableRegisters) == 0:
            raise CompilationError("Pas de registre disponible")
        register = self.__availableRegisters.pop()
        self.__registerStack.append(register)
        self.__log += f"Registre r{register} occupé.\n"
        return register

    def __UALoutputIsAvailable(self) -> bool:
        """
        :return: vrai si la sortie de l'UAL est libre
        :rtype: bool
        """
        return 0 in self.__availableRegisters or self.__engine.ualOutputIsFree() and self.__availableRegisterExists()

    def __moveMemoryToFreeRegister(self) -> int:
        """Libère la dernière mémoire temporaire utilisée et la déplace dans un registre libre

        :return: numéro du registre destination
        :rtype: int
        :raises: CompilationError si aucune mémoire à libérer
        """
        if self.__memoryStackLastIndex < 0:
            raise CompilationError("Pas de données en mémoire disponible")
        destinationRegister = self.__getAvailableRegister()
        memoryVariable = Variable("_m"+str(self.__memoryStackLastIndex))
        self.__log += f"Mémoire {self.__memoryStackLastIndex} chargée dans r{destinationRegister}\n"
        self.__asmManager.pushLoad(self.__lineNumber, memoryVariable, destinationRegister)
        self.__memoryStackLastIndex -= 1
        return destinationRegister

    def __moveTopStackRegisterToMemory(self) -> None:
        """Libère le registre en haut de la pile des registres utilisés.
        Copie le contenu dans une mémoire temporaire.
        Place -1 dans la pile des registres utilisés pour indiquer le placement en mémoire temporaire.
        """
        sourceRegister = self.__getTopStackRegister()
        assert 0 <= sourceRegister < self.__registersNumber
        self.__copyRegisterToMemory(sourceRegister)
        self.__freeRegister()
        self.__registerStack.append(-1)

    def __copyRegisterToMemory(self, sourceRegister:int) -> None:
        """Ajoute au code assembleur l'opération consistant à déplacer un registre vers la mémoire.
        **Ne libère pas le registre**.

        :param sourceRegister: numéro du registre à déplacer
        :type sourceRegister: int
        """

        self.__memoryStackLastIndex +=1
        memoryVariable = Variable("_m"+str(self.__memoryStackLastIndex))
        self.__log += f"Registre r{sourceRegister} chargé dans la mémoire {self.__memoryStackLastIndex}\n"
        self.__asmManager.pushStore(self.__lineNumber, sourceRegister, memoryVariable)

    def __freeZeroRegister(self) -> None:
        """Libère spécifiquement le registre 0, même s'il n'est pas au sommet de la pile.
        Aucune opération s'il est libre.
        """
        if not 0 in self.__registerStack:
            return
        index0 = self.__registerStack.index(0)
        if len(self.__availableRegisters) == 0:
            self.__copyRegisterToMemory(0)
            self.__registerStack[index0] = -1
        else:
            destinationRegister = self.__availableRegisters.pop()
            self.__registerStack[index0] = destinationRegister
            self.__log += f"Libération registre r0 vers r{destinationRegister}\n"
            self.__asmManager.pushMove(self.__lineNumber, 0, destinationRegister)

    ### public
    def resetMemory(self) -> None:
        """Réinitialise les items mémoires du compilateur.
        """
        self.__availableRegisters = list(reversed(range(self.__registersNumber)))
        self.__registerStack = []
        self.__memoryStackLastIndex = -1

    def pushBinaryOperator(self, operator:str, directOrder:bool) -> None:
        """Ajoute une opération binaire.
        Libère les 2 registres au sommet de la pile, ajoute l'opération,
        Occupe le premier registre libre pour le résultat

        :param operator: opération parmi ``+``, ``-``, ``*``, ``/``, ``%``, ``&``, ``|``, ``^``
        :type operator: str
        :param directOrder: vrai si le calcul est donné dans l'ordre, c'est à dire si le haut de la pile correspond au 2e opérande
        :type directOrder: bool
        """

        # Attention ici : ne pas libérer le premier registre tant que les 2e n'a pas été traité
        # -> il faut les libérer en même temps
        if len(self.__registerStack) < 2:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        rLastCalc = self.__getTopStackRegister()
        self.__swapStackRegister()
        rFirstCalc = self.__getTopStackRegister()
        self.__swapStackRegister()
        self.__freeRegister()
        self.__freeRegister()

        if directOrder:
            op1, op2 = rFirstCalc, rLastCalc
        else:
            op1, op2 = rLastCalc, rFirstCalc
        if operator == "cmp":
            self.__asmManager.pushCmp(self.__lineNumber, op1, op2)
        else:
            registreDestination = self.__getAvailableRegister()
            self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (op1, op2), None)

    def pushBinaryOperatorWithLitteral(self, operator:str, litteral:Litteral) -> None:
        """Ajoute une opération binaire dont le 2e opérand est un littéral
        Libère le registre au sommet de la pile comme 1er opérande.
        Occupe le premier registre libre pour le résultat.

        :param operator: opération parmi ``+``, ``-``, ``*``, ``/``, ``%``, ``&``, ``|``, ``^``
        :type operator: str
        :param litteral: littéral
        :type litteral: Litteral
        """
        if len(self.__registerStack) < 1:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        registreOperand = self.__getTopStackRegister()
        self.__freeRegister()
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (registreOperand,), litteral)

    def pushUnaryOperator(self, operator:str) -> None:
        """Ajoute une opération unaire
        Libère le registre au sommet de la pile comme opérande.
        Occupe le premier registre libre pour le résultat.

        :param operator: opération parmi ``~``, ``-``
        :type operator: str
        """
        if len(self.__registerStack) < 1:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        registreOperand = self.__getTopStackRegister()
        self.__freeRegister()
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (registreOperand,), None)

    def pushUnaryOperatorWithLitteral(self, operator:str, litteral:Litteral) -> None:
        """Ajoute une opération unaire dont l'opérande est un littéral
        Occupe le premier registre libre pour le résultat

        :param operator: opération parmi ``~``, ``-``
        :type operator: str
        :param litteral: littéral
        :type litteral: Litteral
        """
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (), litteral)

    def pushValue(self, value:Union[Litteral,Variable]) -> None:
        """Charge une valeur dans le premier registre disponible

        :param value: valeur à charger
        :type value: Union[Litteral,Variable]
        """
        registreDestination = self.__getAvailableRegister()
        if isinstance(value, Litteral):
            self.__asmManager.pushMoveLitteral(self.__lineNumber, value, registreDestination)
        else:
            self.__asmManager.pushLoad(self.__lineNumber, value, registreDestination)

    def getNeededRegisterSpace(self, cost: int, needUAL:bool) -> None:
        """Déplace des registres au besoin
        * Déplace le registre 0 s'il est nécessaire pour l'UAL.
        * Déplace les registres vers la mémoire autant que possible ou nécessaire

        :param cost: cout en registre du noeud d'opération nen cours
        :type cost: int
        :param needUAL: le noeud nécessitera-t-il l'utilisation de l'UAL ?
        :type needUAL: bool
        """
        while cost > len(self.__availableRegisters) and len(self.__availableRegisters) < self.__registersNumber:
            self.__moveTopStackRegisterToMemory()
        if needUAL and not self.__UALoutputIsAvailable():
            self.__freeZeroRegister()

    def stringMemoryUsage(self) -> str:
        """
        :return: représentation de l'occupation actuelle de la mémoire.
        :rtype: str
        """
        strAvailableRegisters = ", ".join(["r"+str(it) for it in self.__availableRegisters])
        strStackedRegisters = ", ".join([str(it) for it in self.__registerStack])
        return f"available = [{strAvailableRegisters}] ; stacked = [{strStackedRegisters}]"

    def __str__ (self) -> str:
        """Transtypage -> str

        :return: log des opérations effectuées
        :rtype: str
        """
        return self.__log

    def getResultRegister(self) -> int:
        """
        :return: registre en haut de la pile
        :rtype: int
        """
        return self.__getTopStackRegister()

    def getEngine(self) -> ProcessorEngine:
        """Accesseur

        :return: modèle de processeur utilisé
        :rtype: ProcessorEngine
        """
        return self.__engine


    """
    zone expérimentale
    """
    def compile(self, node:ExpressionNode) -> List[Tuple[str,Union[Variable,Litteral,None]]]:
        if node.getType() != 'int' and node.isComplexeCondition():
            raise CompilationError(f"{str(self)} n'est pas une expression arithmétique ou une comparaison simple.")
        return self.aux_compile(node)

    def aux_compile(self, node:ExpressionNode) -> Tuple[int,List[Tuple[str,Union[Variable,Litteral,None]]]]:
        if isinstance(node, BinaryNode):
            operator = node.getOperator()
            operand1, operand2 = node.getOperands()
            cost_for_op1, pile_for_op1 = self.aux_compile(operand1)
            op2TryValue = operand2.getValue()
            if isinstance(op2TryValue,Litteral) and self.__engine.litteralOperatorAvailable(operator, op2TryValue):
                pile_for_op1.append((operator, op2TryValue))
                return cost_for_op1, pile_for_op1
            cost_for_op2, pile_for_op2 = self.aux_compile(operand2)
            if cost_for_op1 >= cost_for_op2:
                cost = max(cost_for_op1, cost_for_op2 + 1)
                pile = pile_for_op1 + pile_for_op2
            else:
                cost = max(cost_for_op2, cost_for_op1 + 1)
                pile = pile_for_op2 + pile_for_op1
                pile.append(("swap", None))
            pile.append((operator,None))
            return cost, pile
        if isinstance(node, UnaryNode):
            operator = node.getOperator()
            operand = node.getOperand()
            opTryValue = operand.getValue()
            if isinstance(opTryValue,Litteral) and self.__engine.litteralOperatorAvailable(operator, opTryValue):
                pile = [(operator, opTryValue)]
                return 1, pile
            cost_for_op, pile_for_op = self.aux_compile(operand)
            pile_for_op.append((operator, None))
            return cost_for_op, pile_for_op
        if isinstance(node, ValueNode):
            return 1, [("value", node.getValue())]
        # par défaut
        return 0, []




if __name__=="__main__":
    from assembleurcontainer import AssembleurContainer
    from processorengine import ProcessorEngine
    engine = ProcessorEngine()
    asm = AssembleurContainer(engine)
    """
    cem = CompileExpressionManager(engine, asm, -1)
    cem.pushValue(Variable("x"))
    cem.pushValue(Litteral(5))
    cem.pushBinaryOperator("+", True)
    cem.getNeededRegisterSpace(2,True)
    cem.pushValue(Litteral(3))
    cem.pushValue(Litteral(5))
    cem.pushBinaryOperator("*", True)
    cem.pushBinaryOperator("/", True)
    print(asm)
    """
    """expérimental"""
    print("Exploration autour de la production d'une pile d'exécution")
        #Vérification de base
    from expressionparser import ExpressionParser
    node = ExpressionParser().buildExpression("3*(8+5)-7*6")
    print(str(node))
    cem = CompileExpressionManagerExp(engine, asm, -1)
    cout, pile = cem.compile(node)
    for item,val in pile:
        print(item,",",str(val))

