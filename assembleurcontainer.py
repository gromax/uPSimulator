'''
Classe contenant le code assembleur et permettant des sorties sous diverse formes
'''

class AssembleurLine:
    __label = ""
    __command = ""
    __opcode = ""
    __lineNumber = 0
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

    def isEmpty(self):
        return self.__label == "" and self.__command == ""

    def __str__(self):
        opeStr = [str(op) for op in self.__operands]
        return self.__label+"\t "+self.__command+" "+", ".join(opeStr)


class AssembleurContainer:
    def __init__(self):
        self.__lines = []

    def pushLine(self, attributes):
        newLine = AssembleurLine(attributes)
        self.__lines.append(newLine)

    def __str__(self):
        listStr = [str(item) for item in self.__lines]
        return "\n".join(listStr)

