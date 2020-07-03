"""
.. module:: processor16bitsengine
   :synopsis: Exemple de modèle de processeur
"""

from processorengine import ProcessorEngine, Commands
from operators import Operators, Operator

from typing import Dict

class Processor16Bits(ProcessorEngine):
    _name                  :str = "Processeur 16 bits"
    _register_address_bits :int = 3
    _data_bits             :int = 16
    _freeUalOutput         :bool = True
    _litteralMaxSize       :int = 6
    _litteralsCommands     :Dict[Operator,Commands] = {
            Operators.NEG.value    : { "opcode":"010110", "asm":"NEG" },
            Operators.MOVE.value   : { "opcode":"01001", "asm":"MOVE" },
            Operators.ADD.value    : { "opcode":"1000", "asm":"ADD" },
            Operators.MINUS.value  : { "opcode":"1001", "asm":"SUB" },
            Operators.MULT.value   : { "opcode":"1010", "asm":"MULT" },
            Operators.DIV.value    : { "opcode":"1011", "asm":"DIV" },
            Operators.MOD.value    : { "opcode":"1100", "asm":"MOD" },
            Operators.AND.value    : { "opcode":"1101", "asm":"AND" },
            Operators.OR.value     : { "opcode":"1110", "asm":"OR" },
            Operators.XOR.value    : { "opcode":"1111", "asm":"XOR" },
            Operators.INVERSE.value: { "opcode":"010111", "asm":"NOT" }
    }
    _commands              :Dict[Operator,Commands] = {
            Operators.HALT.value:   { "opcode":"00000", "asm":"HALT" },
            Operators.GOTO.value:   { "opcode":"00001", "asm":"JMP" },
            Operators.NOTEQ.value:  { "opcode":"0001000", "asm":"BNE" },
            Operators.EQ.value:     { "opcode":"0001001", "asm":"BEQ" },
            Operators.INF.value:    { "opcode":"0001010", "asm":"BLT" },
            Operators.SUP.value:    { "opcode":"0001011", "asm":"BGT" },
            Operators.CMP.value:    { "opcode":"00011", "asm":"CMP" },
            Operators.PRINT.value:  { "opcode":"00100", "asm":"PRINT" },
            Operators.INPUT.value:  { "opcode":"00101", "asm":"INPUT" },
            Operators.LOAD.value:   { "opcode":"0011", "asm":"LOAD" },
            Operators.MOVE.value:   { "opcode":"01000", "asm":"MOVE" },
            Operators.NEG.value:    { "opcode":"010100", "asm":"NEG"},
            Operators.INVERSE.value:{ "opcode":"010101", "asm":"NOT"},
            Operators.ADD.value:    { "opcode":"0110000", "asm":"ADD"},
            Operators.MINUS.value:  { "opcode":"0110001", "asm":"SUB"},
            Operators.MULT.value:   { "opcode":"0110010", "asm":"MULT"},
            Operators.DIV.value:    { "opcode":"0110011", "asm":"DIV"},
            Operators.MOD.value:    { "opcode":"0110100", "asm":"MOD"},
            Operators.AND.value:    { "opcode":"0110101", "asm":"AND"},
            Operators.OR.value:     { "opcode":"0110110", "asm":"OR"},
            Operators.XOR.value:    { "opcode":"0110111", "asm":"XOR"},
            Operators.STORE.value:  { "opcode":"0111", "asm":"STORE"}
    }



if __name__=="__main__":
    import doctest
    doctest.testmod()
