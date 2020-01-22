from errors import *

ENGINE_COLLECTION = {
    "default": {
        "register_bits":3,
        "free_ual_output": True,
        "bigLitteralIsNextLine": True,
        "data_bits": 16,
        "litteralCommands":{
            "neg":  { "opcode":"010110", "asm":"NEG", "opnumber":2},
            "move": { "opcode":"01001", "asm":"MOVE", "opnumber":2 },
            "+":    { "opcode":"1000", "asm":"ADD", "opnumber":3},
            "-":    { "opcode":"1001", "asm":"SUB", "opnumber":3},
            "*":    { "opcode":"1010", "asm":"MULT", "opnumber":3},
            "/":    { "opcode":"1011", "asm":"DIV", "opnumber":3},
            "%":    { "opcode":"1100", "asm":"MOD", "opnumber":3},
            "&":    { "opcode":"1101", "asm":"AND", "opnumber":3},
            "|":    { "opcode":"1110", "asm":"OR", "opnumber":3},
            "^":    { "opcode":"1111", "asm":"XOR", "opnumber":3},
            "~":    { "opcode":"010111", "asm":"NOT", "opnumber":2}
        },
        "commands": {
            "halt":   { "opcode":"00000", "asm":"HALT" },
            "goto":   { "opcode":"00001", "asm":"JMP" },
            "!=":     { "opcode":"0001000", "asm":"BNE" },
            "==":     { "opcode":"0001001", "asm":"BEQ" },
            "<":      { "opcode":"0001010", "asm":"BLT" },
            ">":      { "opcode":"0001011", "asm":"BGT" },
            "cmp":    { "opcode":"00011", "asm":"CMP" },
            "print":  { "opcode":"00100", "asm":"PRINT" },
            "input":  { "opcode":"00101", "asm":"INPUT" },
            "load":   { "opcode":"0011", "asm":"LOAD" },
            "move":   { "opcode":"01000", "asm":"MOVE" },
            "neg":    { "opcode":"010100", "asm":"NEG"},
            "~":      { "opcode":"010101", "asm":"NOT"},
            "+":      { "opcode":"0110000", "asm":"ADD"},
            "-":      { "opcode":"0110001", "asm":"SUB"},
            "*":      { "opcode":"0110010", "asm":"MULT"},
            "/":      { "opcode":"0110011", "asm":"DIV"},
            "%":      { "opcode":"0110100", "asm":"MOD"},
            "&":      { "opcode":"0110101", "asm":"AND"},
            "|":      { "opcode":"0110110", "asm":"OR"},
            "^":      { "opcode":"0110111", "asm":"XOR"},
            "store":  { "opcode":"0111", "asm":"STORE"}
        }
    },
    "12bits": {
        "register_bits":2,
        "data_bits": 12,
        "commands": {
            "halt":   { "opcode":"0000", "asm":"HALT" },
            "goto":   { "opcode":"0001", "asm":"JMP" },
            "==":    { "opcode":"0010", "asm":"BEQ" },
            "<":    { "opcode":"0011", "asm":"BLT" },
            "cmp":    { "opcode":"11110101", "asm":"CMP" },
            "print":  { "opcode":"0100", "asm":"PRINT" },
            "input":  { "opcode":"0101", "asm":"INPUT" },
            "load":   { "opcode":"100", "asm":"LOAD" },
            "move":   { "opcode":"11110110", "asm":"MOVE" },
            "~":      { "opcode":"11110111", "asm":"NOT" },
            "+":      { "opcode":"11111000", "asm":"ADD" },
            "-":      { "opcode":"11111001", "asm":"SUB" },
            "*":      { "opcode":"11111010", "asm":"MULT" },
            "/":      { "opcode":"11111011", "asm":"DIV" },
            "%":      { "opcode":"11111100", "asm":"MOD" },
            "&":      { "opcode":"11111101", "asm":"AND" },
            "|":      { "opcode":"11111110", "asm":"OR" },
            "^":      { "opcode":"11111111", "asm":"XOR" },
            "store":  { "opcode":"101", "asm":"STORE" }
        }
    }
}

class Register:
    def __init__(self, index, isUalOnlyOutput):
        self.__index = index
        self.isUalOnlyOutput = __isUalOnlyOutput == True

    def __str__(self):
        return "r"+str(self.__index)

class ProcessorEngine:
    def __init__(self, name = "default"):
        '''
        name = string = nom du modèle
        '''
        if not name in ENGINE_COLLECTION:
          name = "default"
        self.__attributes = ENGINE_COLLECTION[name]
        if "litteralCommands" in self.__attributes:
          self.__litteralsCommands = self.__attributes["litteralCommands"]
        else:
          self.__litteralsCommands = {}
        if "commands" in self.__attributes:
          self.__commands = self.__attributes["commands"]
        else:
          self.__commands = {}

        assert self.__checkAttributes() == True

    def __checkAttributes(self):
        if not "register_bits" in self.__attributes or not isinstance(self.__attributes["register_bits"],int) or self.__attributes["register_bits"] < 1:
          raise AttributeError("Attribut 'register_bits' manquant ou incorrect")
        if not "data_bits" in self.__attributes or not isinstance(self.__attributes["data_bits"],int) or self.__attributes["data_bits"] < 1:
          raise AttributeError("Attribut 'data_bits' manquant ou incorrect")
        for item in self.__litteralsCommands.values():
          if not "opnumber" in item:
              raise AttributeError("Toutes les commandes acceptant un litteral doivent avoir un attribut opnumber")
          if not "opcode" in item:
              raise AttributeError("Toutes les commandes doivent avoir un attribut opcode")
          if not "asm" in item:
              raise AttributeError("Toutes les commandes doivent avoir un attribut asm")
        for item in self.__commands.values():
          if not "opcode" in item:
              raise AttributeError("Toutes les commandes doivent avoir un attribut opcode")
          if not "asm" in item:
              raise AttributeError("Toutes les commandes doivent avoir un attribut asm")

        return True

    def registersNumber(self):
        return 2**self.__attributes["register_bits"]

    def ualOutputIsFree(self):
        return "free_ual_output" in self.__attributes and (self.__attributes["free_ual_output"] == True or self.__attributes["free_ual_output"] == 1)

    def hasNEG(self):
        return "neg" in self.__commands

    def hasOperator(self, operator):
        return operator in self.__commands

    def getRegisterList(self):
        '''
        génère une liste de registre disponibles à usage d'un manager de compilation
        '''
        if self.ualOutputIsFree():
            r0 = Register(0,False)
        else:
            r0 = Register(0,True)
        regs = [r0]
        for i in range(1,self.registersNumber()):
            regs.append(Register(i,False))
        return regs.reverse()

    def getAsmCommand(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour asm, None si n'existe pas
        '''
        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["asm"]

    def getOpcode(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour opcode, None si n'existe pas
        '''
        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["opcode"]

    def getLitteralAsmCommand(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande, version littéral
        sortie = string pour asm, None si n'existe pas
        '''
        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["asm"]

    def getLitteralOpcode(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande, version littéral
        sortie = string pour opcode, None si n'existe pas
        '''
        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["opcode"]

    def litteralOperatorAvailable(self, operator, litteral):
        '''
        operator = nom d'une opération arithmétique ou logique
        litteral = objet Litteral
        Retourne True si l'opérateur existe en version littéral
        et qu'il est possible de l'utiliser avec ce littéral.
        Le cas où ce ne serait pas possible serait celui où le littéral
        serait trop grand et que l'on ne prévoirait pas de le placer à la ligne suivante.
        '''
        if not operator in self.__litteralsCommands:
            return False
        if self.bigLitteralIsNextLine():
            return True
        maxLitteralSize = self.getLitteralMaxSizeIn(operator)
        return litteral.isBetween(0, maxLitteralSize)

    def bigLitteralIsNextLine(self):
        if "bigLitteralIsNextLine" in self.__attributes:
            return self.__attributes["bigLitteralIsNextLine"] == True
        return False

    def getLitteralMaxSizeIn(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        retourne la taille du litteral maximum dans une commande
        '''
        assert commandDesc in self.__litteralsCommands
        commandAttributes = self.__litteralsCommands[commandDesc]
        # on suppose toujours que le littéral peut occuper toute la place restante
        # il faut calculer la place disponible
        nbits_total = self.__attributes["data_bits"]
        nbits_reg = self.__attributes["register_bits"]
        nb_reg_operands = commandAttributes["opnumber"] - 1
        opcode = commandAttributes["opcode"]
        nbits = nbits_total - nb_reg_operands * nbits_reg - len(opcode)
        if nbits <=0:
            raise AttributeError(f"Pas assez de place pour un littéral dans {commandDesc}.")
        return 2**nbits - 2

    def getComparaisonSymbolsAvailables(self):
        '''
        Retourne la liste des symbole de comparaison disponibles dans le modèle
        '''
        symbols = ["<=", "<", ">=", ">", "==", "!="]
        return [item for item in symbols if item in self.__commands]

    def getRegBits(self):
        return self.__attributes["register_bits"]

    def getDataBits(self):
        return self.__attributes["data_bits"]


if __name__=="__main__":
    engine = ProcessorEngine()
