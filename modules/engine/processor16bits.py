"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from typing import Tuple

from modules.engine.processorengine import ProcessorEngine
from modules.primitives.operators import Operators, Operator
from modules.primitives.actionsfifo import ActionType, ActionsFIFO
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.engine.asmgenerator import AsmGenerator ,AsmGenerator_SINGLE, AsmGenerator_TRANSFERT, AsmGenerator_CONDITIONAL_GOTO

from modules.engine.decode import Decodeur, ArgsType

'''
littéraux
NEG     : 010110##########
INVERSE : 010111##########
ADD     : 1000############
MINUS   : 1001############
MULT    : 1010############
DIV     : 1011############
MOD     : 1100############
AND     : 1101############
OR      : 1110############
XOR     : 1111############
MOVE    : 01001###########
autres
HALT    : 0000XXXXXXXXXXXX
NEG     : 010100XXXX######
INVERSE : 010101XXXX######
ADD     : 0110000#########
MINUS   : 0110001#########
MULT    : 0110010#########
DIV     : 0110011#########
MOD     : 0110100#########
AND     : 0110101#########
OR      : 0110110#########
XOR     : 0110111#########
HALT    : 00000XXXXXXXXXXX
GOTO    : 00001###########
NOTEQ   : 0001000#########
EQ      : 0001001#########
INF     : 0001010#########
SUP     : 0001011#########
CMP     : 00011XXXXX######
PRINT   : 00100XXXXXXXX###
INPUT   : 00101XX#########
LOAD    : 0011############
MOVE    : 01000XXXXX######
STORE   : 0111############
'''

class Processor16Bits(ProcessorEngine):
    _name                  :str = "Processeur 16 bits"
    _register_address_bits :int = 3
    _data_bits             :int = 16
    _freeUalOutput         :bool = True
    _litteralDomain        :Tuple[int,int] = (0,63)
    
    _comparaisonOperators = [
        Operators.NOTEQ,
        Operators.EQ,
        Operators.INF,
        Operators.SUP
    ]

    _asmGenerators: Tuple[AsmGenerator, ...] = (
        AsmGenerator_TRANSFERT(Operators.NEG,     "NEG",   "010110.3.7",     operands = [Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.INVERSE, "NOT",   "010111.3.7",     operands = [Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.ADD,     "ADD",   "1000.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.MINUS,   "SUB",   "1001.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.MULT,    "MULT",  "1010.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.DIV,     "DIV",   "1011.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.MOD,     "MOD",   "1100.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.AND,     "AND",   "1101.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.OR,      "OR",    "1110.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.XOR,     "XOR",   "1111.3.3.6",     operands = [Register, Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.MOVE,    "MOVE",  "01001.3.8",      operands = [Litteral, Register]),
        AsmGenerator_TRANSFERT(Operators.NEG,     "NEG",   "010100#4#.3.3",  operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.INVERSE, "NOT",   "010101#4#.3.3",  operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.ADD,     "ADD",   "0110000.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MINUS,   "SUB",   "0110001.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MULT,    "MULT",  "0110010.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.DIV,     "DIV",   "0110011.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MOD,     "MOD",   "0110100.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.AND,     "AND",   "0110101.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.OR,      "OR",    "0110110.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.XOR,     "XOR",   "0110111.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "MOVE",  "01000#5#.3.3",   operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.PRINT,   "PRINT", "00100#8#.3",     operands = [Register]),
        AsmGenerator_TRANSFERT(Operators.INPUT,   "INPUT", "00101#2#.9",      operands = [Variable]),
        AsmGenerator_TRANSFERT(Operators.LOAD,    "LOAD",  "0011.3.9",       operands = [Variable, Register]),
        AsmGenerator_TRANSFERT(Operators.STORE,   "STORE", "0111.9.3",       operands = [Register, Variable]),
        AsmGenerator_SINGLE(Operators.HALT,       "HALT",  "0000#12"),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "JMP",   "00001.11",       operands = [Label]),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BNE", "00011#5#.3.3.0001000.9", comparator = Operators.NOTEQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BEQ", "00011#5#.3.3.0001001.9", comparator = Operators.EQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BLT", "00011#5#.3.3.0001010.9", comparator = Operators.INF),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BGT", "00011#5#.3.3.0001011.9", comparator = Operators.SUP)
    )

    _decodeurs: Tuple[Decodeur,...] = (
        Decodeur("010110##########", Operators.NEG, (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 7)),
        Decodeur("010111##########", Operators.INVERSE, (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 7)),
        Decodeur("1000############", Operators.ADD, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1001############", Operators.MINUS, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1010############", Operators.MULT, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1011############", Operators.DIV, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1100############", Operators.MOD, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1101############", Operators.AND, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1110############", Operators.OR, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("1111############", Operators.XOR, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 6)),
        Decodeur("01001###########", Operators.MOVE, (ArgsType.REGISTRE, 3), (ArgsType.LITTERAL, 8)),
        Decodeur("010100XXXX######", Operators.NEG, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("010101XXXX######", Operators.INVERSE, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110000#########", Operators.ADD, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110001#########", Operators.MINUS, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110010#########", Operators.MULT, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110011#########", Operators.DIV, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110100#########", Operators.MOD, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110101#########", Operators.AND, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110110#########", Operators.OR, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("0110111#########", Operators.XOR, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("01000XXXXX######", Operators.MOVE, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3)),
        Decodeur("00100XXXXXXXX###", Operators.PRINT, (ArgsType.REGISTRE, 3)),
        Decodeur("00101XX#########", Operators.INPUT, (ArgsType.ADRESSE, 9)),
        Decodeur("0011############", Operators.LOAD, (ArgsType.REGISTRE, 3), (ArgsType.ADRESSE, 9)),
        Decodeur("0111############", Operators.STORE, (ArgsType.ADRESSE, 9), (ArgsType.REGISTRE, 3)),
        Decodeur("0000XXXXXXXXXXXX", Operators.HALT),
        Decodeur("00001###########", Operators.GOTO, (ArgsType.ADRESSE, 11)),
        Decodeur("0001000#########", Operators.NOTEQ, (ArgsType.ADRESSE, 9)),
        Decodeur("0001001#########", Operators.EQ, (ArgsType.ADRESSE, 9)),
        Decodeur("0001010#########", Operators.INF, (ArgsType.ADRESSE, 9)),
        Decodeur("0001011#########", Operators.SUP, (ArgsType.ADRESSE, 9)),
        Decodeur("0011XXXXX#######", Operators.CMP, (ArgsType.REGISTRE, 3), (ArgsType.REGISTRE, 3))
    )


    # hérité
    def litteralOperatorAvailable(self, operator:Operator, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param operator: commande à utiliser
        :type operator: Operator
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool
        """

        if operator in (
            Operators.NEG,
            Operators.INVERSE,
            Operators.ADD,
            Operators.MINUS,
            Operators.MULT,
            Operators.DIV,
            Operators.MOD,
            Operators.AND,
            Operators.OR,
            Operators.XOR  
        ):
            minVal, maxVal = self._litteralDomain
            return litteral.isBetween(minVal, maxVal)
        if operator == Operators.MOVE:
            return litteral.isBetween(0, 255)
        return False
        
