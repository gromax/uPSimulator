#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:20:18 2019

@author: gdesjouis
"""

from errors import *

class CompileExpressionManager:
    def __init__(self, options={}):
        if "maxRegisters" in options:
            self.__maxRegisters = options["maxregisters"]
        else:
            self.__maxRegisters = 2
        if "freeUALOutput" in options:
            self.__freeUALOuptut = options["freeUALOutput"]
        else:
            self.__freeUALOuptut = True
        if "litteralInCommand" in options:
            self.litteralInCommand = options["litteralInCommand"]
        else:
            self.litteralInCommand = False
        assert self.__maxRegisters > 1
        self.__availableRegisters = list(reversed(range(self.__maxRegisters)))
        self.__registerStack = []
        self.__operationList = []
        self.__memoryStackLastIndex = -1
        self.__memoryStackMaxIndex = -1

    def availableRegisterExists(self):
        '''
        Sortie : True si au moins un registre est disponible
        '''
        return len(self.__availableRegisters) > 0

    def getAvailableRegister(self):
        if len(self.__availableRegisters) == 0:
            raise CompilationError("Pas de registre disponible")
        register = self.__availableRegisters.pop()
        self.__registerStack.append(register)
        return register

    def freeRegister(self):
        if len(self.__registerStack) == 0:
            raise CompilationError("Aucun registre à libérer.")
        register = self.__registerStack.pop()
        if register == -1:
            self.moveMemoryToFreeRegister()
            register = self.__registerStack.pop()
        self.__availableRegisters.append(register)
        return register

    def freeZeroRegister(self):
        if not 0 in self.__registerStack:
            raise CompilationError("Registre 0 n'est pas occupé.")
        index0 = self.__registerStack.index(0)
        del self.__registerStack[index0]

    def addNewOperation(self,operation):
        self.__operationList.append(operation)

    def pushBinaryOperator(self, operator, directOrder):
        if len(self.__registerStack) < 2:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        '''
         Attention ici !!!
         On ne doit pas libérer rLastCalc avant d'avoir traiter rFirstCalc.
         L'opération rLastCalc = freeRegister() ferait comme si rLastCalc était libre pour les éventuelles
         manipulations de rFirstCalc. Ce n'est pas le cas. Les deux registres ne sont libérés qu'au moment de l'opération.
        '''
        rLastCalc = self.__registerStack[-1]
        if rLastCalc < 0:
            self.__registerStack.pop()
            rLastCalc = self.moveMemoryToFreeRegister()
        rFirstCalc = self.__registerStack[-2]
        if rFirstCalc < 0:
            del self.__registerStack[-2]
            rFirstCalc = self.moveMemoryToFreeRegister()
            '''
            rLastCalc et rFirstCalc peuvent se retrouver dans le désordre dans la pile
            mais c'est sans importance
            '''
        self.freeRegister()
        self.freeRegister()
        registreDestination = self.getAvailableRegister()

        if directOrder:
            operation = (operator, registreDestination, rFirstCalc, rLastCalc)
        else:
            operation = (operator, registreDestination, rLastCalc, rFirstCalc)
        self.addNewOperation(operation)

    def pushBinaryOperatorWithLitteral(self, operator, litteral):
        if len(self.__registerStack) < 1:
            raise CompilationError(f"Pas assez d'opérande pour {operator} dans la pile.")
        registreOperand = self.freeRegister()
        registreDestination = self.getAvailableRegister()
        operation = (operator, registreDestination, registreOperand, litteral)
        self.addNewOperation(operation)

    def pushUnaryOperator(self, operator):
        registreOperand = self.freeRegister()
        registreDestination = self.getAvailableRegister()
        operation = (operator, registreDestination, registreOperand)
        self.addNewOperation(operation)

    def UALoutputIsAvailable(self):
        return self.__freeUALOuptut or 0 in self.__availableRegisters

    def moveRegisterToMemory(self,sourceRegister):
        assert 0 <= sourceRegister < self.__maxRegisters
        self.__memoryStackLastIndex +=1
        operation = ('registre -> memoire', sourceRegister, self.__memoryStackLastIndex)
        self.__operationList.append(operation)
        if self.__memoryStackLastIndex > self.__memoryStackMaxIndex:
            self.__memoryStackMaxIndex = self.__memoryStackLastIndex
        self.__registerStack.append(-1)

    def moveMemoryToFreeRegister(self):
        if self.__memoryStackLastIndex < 0:
            raise CompilationError("Pas de données en mémoire disponible")
        destinationRegister = self.getAvailableRegister()
        operation = ('memoire -> registre', self.__memoryStackLastIndex, destinationRegister)
        self.__operationList.append(operation)
        self.__memoryStackLastIndex -= 1
        return destinationRegister

    def getNeededRegisterSpace(self, cost, needUAL):
        if needUAL and not self.UALoutputIsAvailable():
            if cost > len(self.__availableRegisters):
                self.freeZeroRegister()
                self.moveRegisterToMemory(0)
            else:
                registerTemp = self.getAvailableRegister()
                self.freeZeroRegister()
                operation = ('registre -> registre', 0, registerTemp)
                self.__operationList.append(operation)
        while cost > len(self.__availableRegisters) and len(self.__availableRegisters) < self.__maxRegisters:
            registerToStore = self.freeRegister()
            self.moveRegisterToMemory(registerToStore)

    def stringMemoryUsage(self):
        strAvailableRegisters = ", ".join(["r"+str(it) for it in self.__availableRegisters])
        strStackedRegisters = ", ".join([str(it) for it in self.__registerStack])
        return f"available = [{strAvailableRegisters}] ; stacked = [{strStackedRegisters}]"

    def __str__ (self):
        output = self.stringMemoryUsage()+"\n"
        for item in self.__operationList:
            strItem = ", ".join([str(subItem) for subItem in item])
            output += strItem+"\n"
        return output

if __name__=="__main__":
    cem = CompileExpressionManager()
    cem.getAvailableRegister()
    cem.storeToMemory(5)
    cem.loadFromMemory()
    cem.freeRegister()
    print(cem)

