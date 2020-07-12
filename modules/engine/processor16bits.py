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
littéraux
NEG     : 010110XXXXXXXXXX
INVERSE : 010111XXXXXXXXXX
ADD     : 1000XXXXXXXXXXXX
MINUS   : 1001XXXXXXXXXXXX
MULT    : 1010XXXXXXXXXXXX
DIV     : 1011XXXXXXXXXXXX
MOD     : 1100XXXXXXXXXXXX
AND     : 1101XXXXXXXXXXXX
OR      : 1110XXXXXXXXXXXX
XOR     : 1111XXXXXXXXXXXX
MOVE    : 01001XXXXXXXXXXX
autres
HALT    : 0000XXXXXXXXXXXX
NEG     : 010100XXXXXXXXXX
INVERSE : 010101XXXXXXXXXX
ADD     : 0110000XXXXXXXXX
MINUS   : 0110001XXXXXXXXX
MULT    : 0110010XXXXXXXXX
DIV     : 0110011XXXXXXXXX
MOD     : 0110100XXXXXXXXX
AND     : 0110101XXXXXXXXX
OR      : 0110110XXXXXXXXX
XOR     : 0110111XXXXXXXXX
HALT    : 00000XXXXXXXXXXX
GOTO    : 00001XXXXXXXXXXX
NOTEQ   : 0001000XXXXXXXXX
EQ      : 0001001XXXXXXXXX
INF     : 0001010XXXXXXXXX
SUP     : 0001011XXXXXXXXX
CMP     : 00011XXXXXXXXXXX
PRINT   : 00100XXXXXXXXXXX
INPUT   : 00101XXXXXXXXXXX
LOAD    : 0011XXXXXXXXXXXX
MOVE    : 01000XXXXXXXXXXX
STORE   : 0111XXXXXXXXXXXX
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

    _asmGenerators: List[AsmGenerator] = [
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
        AsmGenerator_TRANSFERT(Operators.NEG,     "NEG",   "010100#4#.3.3", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.INVERSE, "NOT",   "010101#4#.3.3", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.ADD,     "ADD",   "0110000.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MINUS,   "SUB",   "0110001.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MULT,    "MULT",  "0110010.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.DIV,     "DIV",   "0110011.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.MOD,     "MOD",   "0110100.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.AND,     "AND",   "0110101.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.OR,      "OR",    "0110110.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.XOR,     "XOR",   "0110111.3.3.3",  operands = [Register, Register, Register]),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "MOVE",  "01000#5#.3.3", operands = [Register, Register]),
        AsmGenerator_TRANSFERT(Operators.PRINT,   "PRINT", "00100#8#.3", operands = [Register]),
        AsmGenerator_TRANSFERT(Operators.INPUT,   "INPUT", "0010100.9",       operands = [Variable]),
        AsmGenerator_TRANSFERT(Operators.LOAD,    "LOAD",  "0011.3.9",        operands = [Variable, Register]),
        AsmGenerator_TRANSFERT(Operators.STORE,   "STORE", "0111.9.3",        operands = [Register, Variable]),
        AsmGenerator_SINGLE(Operators.HALT,       "HALT",  "#16"),
        AsmGenerator_TRANSFERT(Operators.GOTO,    "JMP",   "00001.11",      operands = [Label]),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BNE", "00011#5#.3.3.0001000.9", comparator = Operators.NOTEQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BEQ", "00011#5#.3.3.0001001.9", comparator = Operators.EQ),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BLT", "00011#5#.3.3.0001010.9", comparator = Operators.INF),
        AsmGenerator_CONDITIONAL_GOTO(Operators.GOTO, "CMP;BGT", "00011#5#.3.3.0001011.9", comparator = Operators.SUP)
    ]



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
        
        