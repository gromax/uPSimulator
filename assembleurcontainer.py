'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

class AssembleurLine:
    __label = ""
    __command = ""
    __opcode = ""
    __lineNumber = 0
    __binary = "?"
    __isLitteral = False
    __isData = False
    def __init__(self, attributes):
        if "label" in attributes:
            self.__label = attributes["label"]
        if "command" in attributes:
            self.__command = attributes["command"]
            assert "opcode" in attributes
            self.__opcode = attributes["opcode"]
        if "operands" in attributes:
            self.__operands = attributes["operands"]
        else:
            self.__operands = []
        if "lineNumber" in attributes:
            self.__lineNumber = attributes["lineNumber"]
        if "binary" in attributes:
            self.__binary = attributes["binary"]
        if "litteral" in attributes:
            self.__isLitteral = True
            self.__litteral = attributes["litteral"]
        if "data" in attributes:
            self.__isData = True
            self.__data = attributes["data"]

    def __str__(self):
        if self.__isLitteral:
            return "LITT\t"+str(self.__litteral)
        if self.__isData:
            return "DATA\t"+str(self.__data)
        opeStr = [str(op) for op in self.__operands]
        return self.__label+"\t "+self.__command+" "+", ".join(opeStr)

    def getBinary(self):
        return self.__binary

class AssembleurContainer:
    def __init__(self):
        self.__lines = []

    def pushLine(self, attributes):
        newLine = AssembleurLine(attributes)
        self.__lines.append(newLine)

    def getBinary(self):
        binaryList = [item.getBinary() for item in self.__lines]
        return "\n".join(binaryList)

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        return "\n".join(listStr)

