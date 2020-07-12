"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from typing import Dict, List, Tuple

from modules.engine.processorengine import ProcessorEngine
from modules.primitives.operators import Operators, Operator
from modules.primitives.actionsfifo import ActionType
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.engine.asmgenerator import AsmGenerator ,AsmGenerator_SINGLE, AsmGenerator_TRANSFERT, AsmGenerator_CONDITIONAL_GOTO

'''
HALT : 000000000000
GOTO : 0001XXXXXXXX
CMP  : 11110101XXXX
BEQ  : 0010XXXXXXXX
BLT  : 0011XXXXXXXX

PRINT   : 0100XXXXXXXX
INPUT   : 0101XXXXXXXX
LOAD    : 100XXXXXXXXX
MOVE    : 11110110XXXX
INVERSE : 11110111XXXX
ADD     : 11111000XXXX
MINUS   : 11111001XXXX
MULT    : 11111010XXXX
DIV     : 11111011XXXX
MOD     : 11111100XXXX
AND     : 11111101XXXX
OR      : 11111110XXXX
XOR     : 11111111XXXX
STORE   : 101XXXXXXXXX
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

    _asmGenerators:List[AsmGenerator] = [
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
        AsmGenerator_SINGLE(Operators.HALT,       "HALT",  "#12"),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "JMP",   "0001.8", operands = [Label]),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BEQ", "11110101.2.2.0010.8", comparator = Operators.EQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BLT", "11110101.2.2.0011.8", comparator = Operators.INF)
    ]



