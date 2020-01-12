#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:20:18 2019

@author: gdesjouis
"""

from errors import *
from variable import Variable
from litteral import Litteral

class CompileExpressionManager:
    def __init__(self, engine, asmManager, lineNumber = -1):
        '''
        engine = objet ProcessorEngine, définit le modèle de processeur utilisé
        asmManager = objet AssembleurContainer, contient le code assembleur final
        lineNumber = int = ligne d'origine de l'expression qui sera compilée
        '''
        self.__engine = engine
        self.__asmManager = asmManager
        self.__lineNumber = lineNumber
        self.__registersNumber = self.__engine.registersNumber()
        assert self.__registersNumber > 1
        self.resetMemory()
        self.log = ""

    ### private
    def __freeRegister(self):
        '''
        Libère le dernier registre de la pile des registres
        Ne doit pas tomber sur un registre mis en mémoire
        retourne le numéro du registre libéré
        '''
        if len(self.__registerStack) == 0:
            self.log += "Erreur : plus de registre à libérer.\n"
            raise CompilationError("Aucun registre à libérer.")
        register = self.__registerStack.pop()
        assert register >= 0
        self.__availableRegisters.append(register)
        self.log += f"Libération de r{register}\n"
        return register

    def __getTopStackRegister(self):
        '''
        Retourne numéro registre au sommet de la pile, sans le libérer.
        Si le numéro est < 0, il s'agit d'une mémoire.
        Provoque le dépilage d'un item de mémoire et retour du numéro registre ayant accueilli le retour
        '''
        if len(self.__registerStack) == 0:
            raise CompilationError("Pas assez d'opérande dans la pile.")
        register = self.__registerStack[-1]
        if register < 0:
            self.__registerStack.pop()
            register = self.__moveMemoryToFreeRegister()
        return register

    def __swapStackRegister(self):
        '''
        Intervertit les contenus des deux derniers étage de la pile des registres
        '''
        if len(self.__registerStack) < 2:
            raise CompilationError("Pas assez d'opérande dans la pile pour swap.")
        op1 = self.__registerStack[-1]
        op2 = self.__registerStack[-2]
        self.__registerStack[-1] = op2
        self.__registerStack[-2] = op1
        self.log += f"Permutation registres (mémoires) {op1} et {op2}\n"

    def __addNewOperation(self,operation):
        self.__operationList.append(operation)

    def __availableRegisterExists(self):
        '''
        Sortie : True si au moins un registre est disponible
        '''
        return len(self.__availableRegisters) > 0

    def __getAvailableRegister(self):
        if len(self.__availableRegisters) == 0:
            raise CompilationError("Pas de registre disponible")
        register = self.__availableRegisters.pop()
        self.__registerStack.append(register)
        self.log += f"Registre r{register} occupé.\n"
        return register

    def __UALoutputIsAvailable(self):
        return self.__engine.ualOutputIsFree() or 0 in self.__availableRegisters

    def __moveMemoryToFreeRegister(self):
        if self.__memoryStackLastIndex < 0:
            raise CompilationError("Pas de données en mémoire disponible")
        destinationRegister = self.__getAvailableRegister()
        memoryVariable = Variable("_m"+str(self.__memoryStackLastIndex))
        self.log += f"Mémoire {self.__memoryStackLastIndex} chargée dans r{destinationRegister}\n"
        self.__asmManager.pushLoad(self.__lineNumber, memoryVariable, desinationRegister)
        self.__memoryStackLastIndex -= 1
        return destinationRegister

    def __moveTopStackRegisterToMemory(self):
        '''
        Libère le registre en haut de la pile des registres
        le déplace vers la mémoire et ajoute -1 dans la pile des registres
        '''
        sourceRegister = self.__getTopStackRegister()
        assert 0 <= sourceRegister < self.__registersNumber
        self.__copyRegisterToMemory(sourceRegister)
        self.__freeRegister()
        self.__registerStack.append(-1)

    def __copyRegisterToMemory(self, sourceRegister):
        '''
        Ajoute l'opération consistant en le déplacement du registre vers la mémoire
        modifie le pointeur mémoire en conséquence
        Ne libère pas le registre
        '''
        self.__memoryStackLastIndex +=1
        memoryVariable = Variable("_m"+str(self.__memoryStackLastIndex))
        self.log += f"Registre r{sourceRegister} chargé dans la mémoire {self.__memoryStackLastIndex}\n"
        self.__asmManager.pushStore(self.__lineNumber, sourceRegister, memoryVariable)

    def __freeZeroRegister(self):
        '''
        libère spécifiquement le registre 0, même s'il n'est pas au sommet de la pile
        Aucune opération si registre 0 inoccupé
        '''
        if not 0 in self.__registerStack:
            return
        index0 = self.__registerStack.index(0)
        if len(self.__availableRegisters) == 0:
            self.__copyRegisterToMemory(0)
            self.__registerStack[index0] = -1
        else:
            destinationRegister = self.__availableRegisters.pop()
            self.__registerStack[index0] = destinationRegister
            self.log += f"Libération registre r0 vers r{destinationRegister}\n"
            self.__asmManager.pushMove(self.__lineNumber, 0, destinationRegister)

    ### public
    def resetMemory(self):
        self.__availableRegisters = list(reversed(range(self.__registersNumber)))
        self.__registerStack = []
        self.__memoryStackLastIndex = -1

    def pushBinaryOperator(self, operator, directOrder):
        '''
        Ajoute une opération binaire.
        operator = +, -, *, /, %, &, |
        directOrder = True si le calcul a été fait dans l'ordre,
        c'est à dire si le top de la pile correspond au 2e opérande.
        Libère les 2 registres au sommet de la pile, ajoute l'opération,
        occupe le premier registre libre pour le résultat
        '''

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
            self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (op1, op2))

    def pushBinaryOperatorWithLitteral(self, operator, litteral):
        '''
        Ajoute une opération binaire dont le 2e opérand est un littéral
        operator = +, -, *, /, %, &, |
        litteral = objet Litteral
        Libère le registre au sommet de la pile comme 1er opérande
        occupe le premier registre libre pour le résultat
        '''
        if len(self.__registerStack) < 1:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        registreOperand = self.__getTopStackRegister()
        self.__freeRegister()
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (registreOperand, litteral))

    def pushUnaryOperator(self, operator):
        '''
        Ajoute une opération unaire
        operator = ~, -
        Libère le registre au sommet de la pile comme opérande
        occupe le premier registre libre pour le résultat
        '''
        if len(self.__registerStack) < 1:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        registreOperand = self.__getTopStackRegister()
        self.__freeRegister()
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (registreOperand,))

    def pushUnaryOperatorWithLitteral(self, operator, litteral):
        '''
        Ajoute une opération unaire dont l'opérande est un littéral
        operator = ~, -
        litteral = Litteral
        occupe le premier registre libre pour le résultat
        '''
        registreDestination = self.__getAvailableRegister()
        self.__asmManager.pushUal(self.__lineNumber, operator, registreDestination, (litteral,))

    def pushValue(self, value):
        '''
        Charge une valeur dans un registre
        value = objet Litteral ou objet Variable
        '''
        registreDestination = self.__getAvailableRegister()
        if isinstance(value, Litteral):
            self.__asmManager.pushMove(self.__lineNumber, value, registreDestination)
        else:
            self.__asmManager.pushLoad(self.__lineNumber, value, registreDestination)

    def getNeededRegisterSpace(self, cost, needUAL):
        '''
        déplace des registres au besoin :
        cost = cout en registre du noeud d'opératio nen cours
        needUAL = True si l'opération en cours utilisera l'UAL
        Déplace le registre 0 s'il est nécessaire pour l'UAL
        déplace les registres vers la mémoire autant que possible ou nécessaire
        '''
        while cost > len(self.__availableRegisters) and len(self.__availableRegisters) < self.__registersNumber:
            self.__moveTopStackRegisterToMemory()
        if needUAL and not self.__UALoutputIsAvailable():
            self.__freeZeroRegister()

    def stringMemoryUsage(self):
        strAvailableRegisters = ", ".join(["r"+str(it) for it in self.__availableRegisters])
        strStackedRegisters = ", ".join([str(it) for it in self.__registerStack])
        return f"available = [{strAvailableRegisters}] ; stacked = [{strStackedRegisters}]"

    def __str__ (self):
        return self.stringMemoryUsage() + "\n" + str(self.__asmManager)

    def getResultRegister(self):
        return self.__getTopStackRegister()

    def getEngine(self):
        return self.__engine


if __name__=="__main__":
    from assembleurcontainer import AssembleurContainer
    from processorengine import ProcessorEngine
    engine = ProcessorEngine()
    asm = AssembleurContainer(engine)
    cem = CompileExpressionManager(engine, asm)
    cem.pushValue(Variable("x"))
    cem.pushValue(Litteral(5))
    cem.pushBinaryOperator("+", True)
    cem.getNeededRegisterSpace(2,True)
    cem.pushValue(Litteral(3))
    cem.pushValue(Litteral(5))
    cem.pushBinaryOperator("*", True)
    cem.pushBinaryOperator("/", True)
    print(asm)

