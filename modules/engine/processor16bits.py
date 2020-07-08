"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from typing import Dict, List, Tuple

from modules.engine.processorengine import ProcessorEngine, Commands
from modules.primitives.operators import Operators, Operator
from modules.primitives.actionsfifo import ActionType
from modules.primitives.litteral import Litteral

class Processor16Bits(ProcessorEngine):
    _name                  :str = "Processeur 16 bits"
    _register_address_bits :int = 3
    _data_bits             :int = 16
    _freeUalOutput         :bool = True
    _litteralDomain        :Tuple[int,int] = (0,63)
    
    _litteralArithmeticsCommands: Dict[Operator,Commands] = {
        Operators.NEG      : { "opcode":"010110", "asm":"NEG" },
        Operators.ADD      : { "opcode":"1000", "asm":"ADD" },
        Operators.MINUS    : { "opcode":"1001", "asm":"SUB" },
        Operators.MULT     : { "opcode":"1010", "asm":"MULT" },
        Operators.DIV      : { "opcode":"1011", "asm":"DIV" },
        Operators.MOD      : { "opcode":"1100", "asm":"MOD" },
        Operators.AND      : { "opcode":"1101", "asm":"AND" },
        Operators.OR       : { "opcode":"1110", "asm":"OR" },
        Operators.XOR      : { "opcode":"1111", "asm":"XOR" },
        Operators.INVERSE  : { "opcode":"010111", "asm":"NOT" }
    }

    _arithmeticsCommands: Dict[Operator,Commands] = {
        Operators.NEG      : { "opcode":"010100", "asm":"NEG"},
        Operators.INVERSE  : { "opcode":"010101", "asm":"NOT"},
        Operators.ADD      : { "opcode":"0110000", "asm":"ADD"},
        Operators.MINUS    : { "opcode":"0110001", "asm":"SUB"},
        Operators.MULT     : { "opcode":"0110010", "asm":"MULT"},
        Operators.DIV      : { "opcode":"0110011", "asm":"DIV"},
        Operators.MOD      : { "opcode":"0110100", "asm":"MOD"},
        Operators.AND      : { "opcode":"0110101", "asm":"AND"},
        Operators.OR       : { "opcode":"0110110", "asm":"OR"},
        Operators.XOR      : { "opcode":"0110111", "asm":"XOR"}
    }

    _litteralsCommands     :Dict[Operator,Commands] = {
         Operators.MOVE     : { "opcode":"01001", "asm":"MOVE" },
    }

    _commands              :Dict[Operator,Commands] = {
        Operators.HALT         : { "opcode":"00000", "asm":"HALT" },
        Operators.GOTO         : { "opcode":"00001", "asm":"JMP" },
        Operators.NOTEQ        : { "opcode":"0001000", "asm":"BNE" },
        Operators.EQ           : { "opcode":"0001001", "asm":"BEQ" },
        Operators.INF          : { "opcode":"0001010", "asm":"BLT" },
        Operators.SUP          : { "opcode":"0001011", "asm":"BGT" },
        Operators.CMP          : { "opcode":"00011", "asm":"CMP" },
        Operators.PRINT        : { "opcode":"00100", "asm":"PRINT" },
        Operators.INPUT        : { "opcode":"00101", "asm":"INPUT" },
        Operators.LOAD         : { "opcode":"0011", "asm":"LOAD" },
        Operators.MOVE         : { "opcode":"01000", "asm":"MOVE" },
        Operators.STORE        : { "opcode":"0111", "asm":"STORE"}
    }

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

        if operator in self._litteralArithmeticsCommands:
            minVal, maxVal = self._litteralDomain
            return litteral.isBetween(minVal, maxVal)
        if operator == Operators.MOVE:
            return litteral.isBetween(0, 255)
        return False
        
        