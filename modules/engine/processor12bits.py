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
            Operators.HALT.value:   { "opcode":"0000", "asm":"HALT" },
            Operators.GOTO.value:   { "opcode":"0001", "asm":"JMP" },
            Operators.EQ.value:     { "opcode":"0010", "asm":"BEQ" },
            Operators.INF.value:    { "opcode":"0011", "asm":"BLT" },
            Operators.CMP.value:    { "opcode":"11110101", "asm":"CMP" },
            Operators.PRINT.value:  { "opcode":"0100", "asm":"PRINT" },
            Operators.INPUT.value:  { "opcode":"0101", "asm":"INPUT" },
            Operators.LOAD.value:   { "opcode":"100", "asm":"LOAD" },
            Operators.MOVE.value:   { "opcode":"11110110", "asm":"MOVE" },
            Operators.INVERSE.value:{ "opcode":"11110111", "asm":"NOT" },
            Operators.ADD.value:    { "opcode":"11111000", "asm":"ADD" },
            Operators.MINUS.value:  { "opcode":"11111001", "asm":"SUB" },
            Operators.MULT.value:   { "opcode":"11111010", "asm":"MULT" },
            Operators.DIV.value:    { "opcode":"11111011", "asm":"DIV" },
            Operators.MOD.value:    { "opcode":"11111100", "asm":"MOD" },
            Operators.AND.value:    { "opcode":"11111101", "asm":"AND" },
            Operators.OR.value:     { "opcode":"11111110", "asm":"OR" },
            Operators.XOR.value:    { "opcode":"11111111", "asm":"XOR" },
            Operators.STORE.value:  { "opcode":"101", "asm":"STORE" }
    }



if __name__=="__main__":
    import doctest
    doctest.testmod()
