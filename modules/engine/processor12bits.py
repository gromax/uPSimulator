"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from typing import Tuple

from modules.engine.processorengine import ProcessorEngine
from modules.primitives.operators import Operators, Operator
from modules.primitives.actionsfifo import ActionType
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.engine.asmgenerator import AsmGenerator ,AsmGenerator_SINGLE, AsmGenerator_TRANSFERT, AsmGenerator_CONDITIONAL_GOTO
from modules.engine.decode import Decodeur, ArgsType


'''
HALT : 0000XXXXXXXX
GOTO : 0001########
CMP  : 11110101####
BEQ  : 0010########
BLT  : 0011########

NEG     : 11110110XX##
INVERSE : 11110111XX##
PRINT   : 0100XXXXXX##
INPUT   : 0101########
LOAD    : 100#########
MOVE    : 11110110####
INVERSE : 11110111####
ADD     : 11111000####
MINUS   : 11111001####
MULT    : 11111010####
DIV     : 11111011####
MOD     : 11111100####
AND     : 11111101####
OR      : 11111110####
XOR     : 11111111####
STORE   : 101#########
'''



class Processor12Bits(ProcessorEngine):
    _name                  :str = "Processeur 12 bits"
    _register_address_bits :int = 2
    _data_bits             :int = 12
    _freeUalOutput         :bool = False
    _litteralDomain        :Tuple[int,int] = (0,0)

    _comparaisonOperators = [
        Operators.EQ,
        Operators.INF
    ]

    _asmGenerators:Tuple(AsmGenerator,...) = [
        AsmGenerator_TRANSFERT(Operators.NEG,     "NEG",   "11110110#2#.0.2", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.INVERSE, "NOT",   "11110111#2#.0.2", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.ADD,     "ADD",   "11111000.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MINUS,   "SUB",   "11111001.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MULT,    "MULT",  "11111010.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.DIV,     "DIV",   "11111011.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MOD,     "MOD",   "11111100.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.AND,     "AND",   "11111101.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.OR,      "OR",    "11111110.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.XOR,     "XOR",   "11111111.0.2.2", operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "MOVE",  "11110110.2.2", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.PRINT,   "PRINT", "0100#6#.2", operands = [Register]),
        AsmGenerator_TRANSFERT(Operators.INPUT,   "INPUT", "0101.8", operands = [Variable]),
        AsmGenerator_TRANSFERT(Operators.LOAD,    "LOAD",  "100.2.7", operands = [Variable, Register]),
        AsmGenerator_TRANSFERT(Operators.STORE,   "STORE", "101.7.2", operands = [Register, Variable]),
        AsmGenerator_SINGLE(Operators.HALT,       "HALT",  "0000#8"),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "JMP",   "0001.8", operands = [Label]),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BEQ", "11110101.2.2.0010.8", comparator = Operators.EQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BLT", "11110101.2.2.0011.8", comparator = Operators.INF)
    ]

    _decodeurs: Tuple[Decodeur,...] = (
        Decodeur("11110110XX##", Operators.NEG, (ArgsType.REGISTRE, 2)),
        Decodeur("11110111XX##", Operators.INVERSE, (ArgsType.REGISTRE, 2)),
        Decodeur("11111000####", Operators.ADD, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111001####", Operators.MINUS, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111010####", Operators.MULT, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111011####", Operators.DIV, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111100####", Operators.MOD, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111101####", Operators.AND, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111110####", Operators.OR, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11111111####", Operators.XOR, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("11110110####", Operators.MOVE, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2)),
        Decodeur("0100XXXXXX##", Operators.PRINT, (ArgsType.REGISTRE, 2)),
        Decodeur("0101########", Operators.INPUT, (ArgsType.ADRESSE, 8)),
        Decodeur("100#########", Operators.LOAD, (ArgsType.REGISTRE, 2), (ArgsType.ADRESSE, 7)),
        Decodeur("101#########", Operators.STORE, (ArgsType.ADRESSE, 7), (ArgsType.REGISTRE, 2)),
        Decodeur("0000XXXXXXXX", Operators.HALT),
        Decodeur("0001########", Operators.GOTO, (ArgsType.ADRESSE, 8)),
        Decodeur("0010########", Operators.EQ, (ArgsType.ADRESSE, 8)),
        Decodeur("0011########", Operators.INF, (ArgsType.ADRESSE, 8)),
        Decodeur("11110101####", Operators.CMP, (ArgsType.REGISTRE, 2), (ArgsType.REGISTRE, 2))
    )

