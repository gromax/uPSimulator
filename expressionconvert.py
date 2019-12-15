#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:20:18 2019

@author: gdesjouis
"""

from errors import *
from expression import *

class CompileExpressionManager:

    def __init__(self):
        self.__maxRegisters = 2
        self.availableRegisters = list(reversed(range(self.__maxRegisters)))
        self.registerStack = []
        self.operationList = []
        self.memory = -1

    def getAvailableRegister(self):
        if len(self.availableRegisters) == 0:
            raise CompilationError(f"Pas de registre disponible'")
        self.registerStack.append(self.availableRegisters.pop())
        return self.registerStack[-1]

    def freeRegister(self):
        r = self.registerStack.pop()
        self.availableRegisters.append(r)
        return r

    def addNewOperation(self,operation):
        self.operationList.append(operation)

    def UALoutputIsAvailable(self):
        return 0 in self.availableRegister

    def storeToMemory(self,cost):
        if cost > len(self.availableRegisters):
            self.memory +=1
            self.operationList.append(('registre -> memoire', self.freeRegister(),self.memory))
            return True
        else:
            return False

    def loadFromMemory(self):
        self.operationList.append(('memoire -> registre', self.memory, self.getAvailableRegister()))
        self.memory -=1

    def compileExpression(self, expression):
        expression.calcCompile(self)
        return self.operationList

