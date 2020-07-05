"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from typing import Dict

from modules.engine.processorengine import ProcessorEngine, Commands
from modules.primitives.operators import Operators, Operator


class Processor12Bits(ProcessorEngine):
    _name                  :str = "Processeur 12 bits"
    _register_address_bits :int = 2
    _data_bits             :int = 12
    _freeUalOutput         :bool = False
    _litteralMaxSize       :int = 0
    _litteralsCommands     :Dict[Operator,Commands] = {}
    _commands              :Dict[Operator,Commands] = {
            Operators.HALT    : { "opcode":"0000", "asm":"HALT" },
            Operators.GOTO    : { "opcode":"0001", "asm":"JMP" },
            Operators.EQ      : { "opcode":"0010", "asm":"BEQ" },
            Operators.INF     : { "opcode":"0011", "asm":"BLT" },
            Operators.CMP     : { "opcode":"11110101", "asm":"CMP" },
            Operators.PRINT   : { "opcode":"0100", "asm":"PRINT" },
            Operators.INPUT   : { "opcode":"0101", "asm":"INPUT" },
            Operators.LOAD    : { "opcode":"100", "asm":"LOAD" },
            Operators.MOVE    : { "opcode":"11110110", "asm":"MOVE" },
            Operators.INVERSE : { "opcode":"11110111", "asm":"NOT" },
            Operators.ADD     : { "opcode":"11111000", "asm":"ADD" },
            Operators.MINUS   : { "opcode":"11111001", "asm":"SUB" },
            Operators.MULT    : { "opcode":"11111010", "asm":"MULT" },
            Operators.DIV     : { "opcode":"11111011", "asm":"DIV" },
            Operators.MOD     : { "opcode":"11111100", "asm":"MOD" },
            Operators.AND     : { "opcode":"11111101", "asm":"AND" },
            Operators.OR      : { "opcode":"11111110", "asm":"OR" },
            Operators.XOR     : { "opcode":"11111111", "asm":"XOR" },
            Operators.STORE   : { "opcode":"101", "asm":"STORE" }
    }



if __name__=="__main__":
    import doctest
    doctest.testmod()
