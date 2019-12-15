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
        self.__availableRegisters.append(register)
        return register

    def addNewOperation(self,operation):
        self.__operationList.append(operation)

    def UALoutputIsAvailable(self):
        return self.__freeUALOuptut or 0 in self.__availableRegisters

    def storeToMemory(self,cost):
        if cost <= len(self.__availableRegisters):
            return False
        self.__memoryStackLastIndex +=1
        sourceRegister = self.freeRegister()
        operation = ('registre -> memoire', sourceRegister, self.__memoryStackLastIndex)
        self.__operationList.append(operation)
        if self.__memoryStackLastIndex > self.__memoryStackMaxIndex:
            self.__memoryStackMaxIndex = self.__memoryStackLastIndex
        return True

    def loadFromMemory(self):
        if self.__memoryStackLastIndex < 0:
            raise CompilationError("Pas de données en mémoire disponible")
        destinationRegister = self.getAvailableRegister()
        operation = ('memoire -> registre', self.__memoryStackLastIndex, destinationRegister)
        self.__operationList.append(operation)
        self.__memoryStackLastIndex -= 1

    def __str__ (self):
        if self.__memoryStackLastIndex >=0:
            output = f"memory stack -> {self.__memoryStackLastIndex}\n"
        else:
            output = "no memory stacked\n"
        if self.availableRegisterExists():
            strAvailableRegisters = ", ".join(["r"+str(item) for item in self.__availableRegisters])
            output += f"availables registers : {strAvailableRegisters}\n"
        else:
            output += "no available register\n"
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

