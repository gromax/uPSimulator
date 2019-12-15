#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:20:18 2019

@author: gdesjouis
"""

from errors import *
from expression import *

class CompileExpressionManager:

    def __init__(self options={}):
        if "maxRegisters" in options:
            self.__maxRegisters = options["maxregisters"]
        else:
            self.__maxRegisters = 2
        self.__availableRegisters = list(reversed(range(self.__maxRegisters)))
        self.__registerStack = []
        self.__operationList = []
        self.__memory = -1

    def getAvailableRegister(self):
        if len(self.__availableRegisters) == 0:
            raise CompilationError("Pas de registre disponible'")
        self.__registerStack.append(self.__availableRegisters.pop())
        return self.__registerStack[-1]

    def freeRegister(self):
        r = self.__registerStack.pop()
        self.__availableRegisters.append(r)
        return r

    def addNewOperation(self,operation):
        self.__operationList.append(operation)

    def UALoutputIsAvailable(self):
        return 0 in self.availableRegister

    def storeToMemory(self,cost):
        if cost > len(self.__availableRegisters):
            self.__memory +=1
            self.__operationList.append(('registre -> memoire', self.freeRegister(),self.__memory))
            return True
        else:
            return False

    def loadFromMemory(self):
        self.__operationList.append(('memoire -> registre', self.__memory, self.getAvailableRegister()))
        self.__memory -= 1

    def compileExpression(self, expression):
        expression.calcCompile(self)
        return self.__operationList

