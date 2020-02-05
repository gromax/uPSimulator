"""
.. module:: processorengine
   :synopsis: classe définissant les attributs d'un modèle de processeur et fournissant les informations utiles aux outils de compilation
"""

from typing import Union, List, Dict, Optional
from typing_extensions import TypedDict

Commands = TypedDict('Commands', {
    'opcode': str,
    'asm': str
})

EngineAttributes = TypedDict('EngineAttributes', {
    'register_bits': int,
    'data_bits': int,
    'free_ual_output':bool,
    'litteralCommands':Dict[str,Commands],
    'commands':Dict[str,Commands]
})



from errors import *
from litteral import Litteral

ENGINE_COLLECTION: Dict[str,EngineAttributes] = {
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
        "free_ual_output": False,
        "data_bits": 12,
        "litteralCommands": {},
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
    __litteralsCommands:Dict[str,Commands] = {}
    __commands:Dict[str,Commands] = {}

    def __init__(self, name:str = "default"):
        """Constructeur

        :param name: nom du modèle de processeur utilisé
        :type name: str
        """
        # TODO: chargement d'un modèle dans un fichier texte
        if not name in ENGINE_COLLECTION:
          name = "default"
        attributes: EngineAttributes = ENGINE_COLLECTION[name]
        if "register_bits" in attributes and isinstance(attributes["register_bits"],int):
            self.__register_address_bits = attributes["register_bits"]
        if "data_bits" in attributes and isinstance(attributes["data_bits"],int):
            self.__data_bits = attributes["data_bits"]
        if "free_ual_output" in attributes:
            self.__freeUalOutput = (attributes["free_ual_output"] == True)

        if "litteralCommands" in attributes:
          self.__litteralsCommands = attributes["litteralCommands"]
        if "commands" in attributes:
          self.__commands = attributes["commands"]

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
        """Vérification de la consistance des attributs du modèle de processeur
        Le configuration doit contenir un register_bits >= 1, data_bits, les commandes d'instructions doivent contenir un opcode et une commande asm

        :return: vrai si les attributs sont corrects
        :rtype: bool
        :raises: AttributeError, en cas d'attributs incorrects.
        """
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
            # vérification de l'espace laissé à un littéral
            nbits_total = self.__data_bits
            nbits_reg = self.__register_address_bits
            nb_reg_operands = self.__opNumber[name] - 1
            opcode = attr["opcode"]
            litteral_bits = nbits_total - nb_reg_operands * nbits_reg - len(opcode)
            if  litteral_bits <= 0:
                raise AttributeError(f"Pas assez de place pour un littéral dans {commandDesc}.")
            else:
                self.__litteralsCommands[name]["litteral_bits"] = litteral_bits
        for item in self.__commands.values():
            if not "opcode" in item:
                raise AttributeError("Toutes les commandes doivent avoir un attribut opcode")
            if not "asm" in item:
                raise AttributeError("Toutes les commandes doivent avoir un attribut asm")

        return True

    def registersNumber(self) -> int:
        """Calcul le nombre de registres considérant l'adressage disponible

        :return: nombre de registre
        :rtype: int

        :Example:
        >>> ProcessorEngine().registersNumber()
        8
        """
        return 2**self.__register_address_bits

    def ualOutputIsFree(self) -> bool:
        """Accesseur

        :return: Vrai si on peut choisir le registre de sortie de l'UAL
        :rtype: bool

        :Example:
        >>> ProcessorEngine().ualOutputIsFree()
        True
        >>> ProcessorEngine("12bits").ualOutputIsFree()
        False
        """
        return self.__freeUalOutput

    def hasNEG(self) -> bool:
        """Le modèle de processeur possède-t-il un - unaire ?

        :return: vrai s'il en possède un
        :rtype: bool

        :Example:
        >>> ProcessorEngine().hasNEG()
        True
        >>> ProcessorEngine("12bits").hasNEG()
        False
        """
        return "neg" in self.__commands

    def hasOperator(self, operator:str) -> bool:
        """Le modèle de processeur possède-t-il l'opérateur demandé ?

        :param operator: nom de l'opérateur
        :type operator: str
        :return: Vrai s'il le possède
        :rtype: bool

        :Example:
        >>> ProcessorEngine().hasOperator("*")
        True
        >>> ProcessorEngine().hasOperator("?")
        False
        """
        return operator in self.__commands

    def getAsmCommand(self, commandDesc:str) -> Optional[str]:
        """Renvoie le nom de commande assembleur de la commande demandée. None si introuvable.

        :param commandDesc: nom de la commande
        :type commandDesc: str
        :return: commande assembleur
        :rtype: str

        :Example:
        >>> ProcessorEngine().getAsmCommand("*")
        'MULT'
        >>> ProcessorEngine().getAsmCommand("&")
        'AND'
        >>> ProcessorEngine().getAsmCommand("?") is None
        True
        """

        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["asm"]

    def getOpcode(self, commandDesc:str) -> Optional[str]:
        """Renvoie l'opcode de la commande demandée. None si introuvable.

        :param commandDesc: nom de la commande
        :type commandDesc: str
        :return: opcode sous forme binaire
        :rtype: str

        :Example:
        >>> ProcessorEngine().getOpcode("*")
        '0110010'
        >>> ProcessorEngine().getOpcode("?") is None
        True
        """

        if not commandDesc in self.__commands:
            return None
        itemAttribute = self.__commands[commandDesc]
        return itemAttribute["opcode"]

    def getLitteralAsmCommand(self, commandDesc:str) -> Optional[str]:
        """Renvoie le nom de commande assembleur de la commande demandée, dans sa version acceptant un littéral. None si introuvable.

        :param commandDesc: nom de la commande
        :type commandDesc: str
        :return: commande assembleur
        :rtype: str

        :Example:
        >>> ProcessorEngine().getLitteralAsmCommand("*")
        'MULT'
        >>> ProcessorEngine().getLitteralAsmCommand("?") is None
        True
        """
        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["asm"]

    def getLitteralOpcode(self, commandDesc:str) -> Optional[str]:
        """Renvoie l'opcode de la commande demandée dans sa version acceptant un littéral. None si introuvable.

        :param commandDesc: nom de la commande
        :type commandDesc: str
        :return: opcode sous forme binaire
        :rtype: str

        :Example:
        >>> ProcessorEngine().getLitteralOpcode("*")
        '1010'
        >>> ProcessorEngine().getLitteralOpcode("?") is None
        True
        """

        if not commandDesc in self.__litteralsCommands:
            return None
        itemAttribute = self.__litteralsCommands[commandDesc]
        return itemAttribute["opcode"]

    def litteralOperatorAvailable(self, commandDesc:str, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param commandDesc: commande à utiliser
        :type commandDesc: str
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool

        :Example:
        >>> ProcessorEngine().litteralOperatorAvailable("*", Litteral(1))
        True
        >>> ProcessorEngine().litteralOperatorAvailable("*", Litteral(10000))
        False
        """

        if not commandDesc in self.__litteralsCommands:
            return False
        maxLitteralSize = self.getLitteralMaxSizeIn(commandDesc)
        return litteral.isBetween(0, maxLitteralSize)

    def getLitteralMaxSizeIn(self, commandDesc:str) -> int:
        """Considérant une commande, détermine le nombre de bits utilisés par l'encodage des attributs de la commande et déduit le nombre de bits laissés pour le codage en nombre positif d'un éventuel littéral, et donc la taille maximal de ce littéral.

        :param commandDesc: commande à utiliser
        :type commandDesc: str
        :return: valeur maximale acceptable du littéral
        :rtype: int

        :Example:
        >>> ProcessorEngine().getLitteralMaxSizeIn("*")
        63
        """

        assert commandDesc in self.__litteralsCommands
        commandAttributes = self.__litteralsCommands[commandDesc]
        # on suppose toujours que le littéral peut occuper toute la place restante
        # il faut calculer la place disponible
        litteral_bits = commandAttributes["litteral_bits"]
        return 2**litteral_bits - 1


    def getComparaisonSymbolsAvailables(self) -> List[str]:
        """Accesseur

        :return: liste des symboles de comparaison disponibles avec ce modèle de processeur
        :rtype: list[str]

        :Example:
        >>> ProcessorEngine().getComparaisonSymbolsAvailables()
        ['<', '>', '==', '!=']
        """

        symbols = ["<=", "<", ">=", ">", "==", "!="]
        return [item for item in symbols if item in self.__commands]

    def getRegBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage de l'adresse d'un registre
        :rtype: int

        :Example:
        >>> ProcessorEngine().getRegBits()
        3
        """
        return self.__register_address_bits

    def getDataBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage d'une donnée en mémoire
        :rtype: int

        :Example:
        >>> ProcessorEngine().getDataBits()
        16
        """
        return self.__data_bits


if __name__=="__main__":
    import doctest
    doctest.testmod()
