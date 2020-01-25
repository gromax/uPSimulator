from typing import Union, List, Dict


from errors import *
from litteral import Litteral

ENGINE_COLLECTION = {
    "default": {
        "register_bits":3,
        "free_ual_output": True,
        "data_bits": 16,
        "litteralCommands":{
            "neg":  { "opcode":"010110", "asm":"NEG" },
            "move": { "opcode":"01001", "asm":"MOVE" },
            "+":    { "opcode":"1000", "asm":"ADD" },
            "-":    { "opcode":"1001", "asm":"SUB" },
            "*":    { "opcode":"1010", "asm":"MULT" },
            "/":    { "opcode":"1011", "asm":"DIV" },
            "%":    { "opcode":"1100", "asm":"MOD" },
            "&":    { "opcode":"1101", "asm":"AND" },
            "|":    { "opcode":"1110", "asm":"OR" },
            "^":    { "opcode":"1111", "asm":"XOR" },
            "~":    { "opcode":"010111", "asm":"NOT" }
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

class ProcessorEngine:
    __register_address_bits = 1
    __data_bits = 0
    __freeUalOutput = False
    def __init__(self, name:str = "default"):
        '''
        name = string = nom du modèle
        '''
        if not name in ENGINE_COLLECTION:
          name = "default"
        attributes = ENGINE_COLLECTION[name]
        if "register_bits" in attributes and isinstance(attributes["register_bits"],int):
            self.__register_address_bits = attributes["register_bits"]
        if "data_bits" in attributes and isinstance(attributes["data_bits"],int):
            self.__data_bits = attributes["data_bits"]
        if "free_ual_output" in attributes:
            self.__freeUalOutput = (attributes["free_ual_output"] == True)

        if "litteralCommands" in attributes:
          self.__litteralsCommands = attributes["litteralCommands"]  # type : Dict
        else:
          self.__litteralsCommands = {}  # type : Dict
        if "commands" in attributes:
          self.__commands = attributes["commands"] # type: Dict
        else:
          self.__commands = {} # type : Dict

        if self.ualOutputIsFree():
            destReg = 1
        else:
            destReg = 0
        self.__opNumber = {
            "neg":  1 + destReg,
            "move": 2,
            "+":    2 + destReg,
            "-":    2 + destReg,
            "*":    2 + destReg,
            "/":    2 + destReg,
            "%":    2 + destReg,
            "&":    2 + destReg,
            "|":    2 + destReg,
            "^":    2 + destReg,
            "~":    1 + destReg
        }

        assert self.__checkAttributes() == True

    def __checkAttributes(self) -> bool:
        if self.__register_address_bits < 1:
            raise AttributeError("Attribut 'register_bits' manquant ou incorrect")
        if self.__data_bits <= 0:
            raise AttributeError("Attribut 'data_bits' manquant ou incorrect")

        for (name, attr) in self.__litteralsCommands.items():
            if not name in self.__opNumber:
                raise AttributeError(f"La commande {name} n'est pas une commande littérale valide.")
            if not "opcode" in attr:
                raise AttributeError("Toutes les commandes doivent avoir un attribut opcode")
            if not "asm" in attr:
                raise AttributeError("Toutes les commandes doivent avoir un attribut asm")
        for item in self.__commands.values():
            if not "opcode" in item:
                raise AttributeError("Toutes les commandes doivent avoir un attribut opcode")
            if not "asm" in item:
                raise AttributeError("Toutes les commandes doivent avoir un attribut asm")

        return True

    def registersNumber(self) -> int:
        return 2**self.__register_address_bits

    def ualOutputIsFree(self) -> bool:
        return self.__freeUalOutput

    def hasNEG(self) -> bool:
        return "neg" in self.__commands

    def hasOperator(self, operator:str) -> bool:
        return operator in self.__commands

    def getAsmCommand(self, commandDesc:str) -> Union[None, str]:
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour asm, None si n'existe pas
        '''
        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["asm"]

    def getOpcode(self, commandDesc:str):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour opcode, None si n'existe pas
        '''
        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["opcode"]

    def getLitteralAsmCommand(self, commandDesc:str) -> Union[None, str]:
        '''
        commandDesc = chaîne de caractère décrivant un type de commande, version littéral
        sortie = string pour asm, None si n'existe pas
        '''
        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["asm"]

    def getLitteralOpcode(self, commandDesc:str) -> Union[None, str]:
        '''
        commandDesc = chaîne de caractère décrivant un type de commande, version littéral
        sortie = string pour opcode, None si n'existe pas
        '''
        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["opcode"]

    def litteralOperatorAvailable(self, operator:str, litteral:Litteral) -> bool:
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
        maxLitteralSize = self.getLitteralMaxSizeIn(operator)
        return litteral.isBetween(0, maxLitteralSize)

    def getLitteralMaxSizeIn(self, commandDesc:str) -> int:
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        retourne la taille du litteral maximum dans une commande
        '''
        assert commandDesc in self.__litteralsCommands
        commandAttributes = self.__litteralsCommands[commandDesc]
        # on suppose toujours que le littéral peut occuper toute la place restante
        # il faut calculer la place disponible
        nbits_total = self.__data_bits
        nbits_reg = self.__register_address_bits
        nb_reg_operands = self.__opNumber[commandDesc] - 1
        opcode = commandAttributes["opcode"]
        nbits = nbits_total - nb_reg_operands * nbits_reg - len(opcode)
        if nbits <=0:
            raise AttributeError(f"Pas assez de place pour un littéral dans {commandDesc}.")
        return 2**nbits - 1


    def getComparaisonSymbolsAvailables(self) -> List[str]:
        '''
        Retourne la liste des symbole de comparaison disponibles dans le modèle
        '''
        symbols = ["<=", "<", ">=", ">", "==", "!="]
        return [item for item in symbols if item in self.__commands]

    def getRegBits(self) -> int:
        return self.__register_address_bits

    def getDataBits(self) -> int:
        return self.__data_bits


if __name__=="__main__":
    engine = ProcessorEngine()
