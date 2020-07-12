"""
.. module:: tests.test_cem
:synopsis: Tests des modules modules.engine
"""

import unittest

from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.litteral import Litteral
from modules.primitives.actionsfifo import ActionsFIFO
from modules.primitives.operators import Operators

from modules.engine.processor16bits import Processor16Bits
from modules.engine.processor12bits import Processor12Bits


from modules.compilemanager import CompilationManager as CM
from modules.parser.code import CodeParser as CP

class AsmSingleLineTest(unittest.TestCase):
    def test1(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        l4 = Litteral(4)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, l4, r0, op)

        asm = engine.getAsm(actions)
        self.assertEqual(asm, "	ADD r0, r1, #4")

    def test2(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, r0, r0, op)

        asm = engine.getAsm(actions)
        self.assertEqual(asm, "	ADD r0, r1, r0")
    
    def test3(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        l4 = Litteral(4)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, l4, r0, op, r1, r0, r0, op)

        asm = engine.getAsm(actions)
        good = "\n".join([
            "	ADD r0, r1, #4",
            "	ADD r0, r1, r0"
        ])
        self.assertEqual(asm, good)

class AsmTest(unittest.TestCase):
    maxDiff = None
    def test1(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor16Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        asm = engine.getAsm(actionsList, False)
        good = "\n".join([
            "	MOVE r7, #0",
            "	STORE @x, r7",
            "	MOVE r7, #0",
            "	STORE @i, r7",
            "Lab2	LOAD r7, @i",
            "	MOVE r6, #10",
            "	CMP r7, r6",
            "	BLT Lab1",
            "	JMP Lab3",
            "Lab1	LOAD r7, @i",
            "	ADD r7, r7, #1",
            "	STORE @i, r7",
            "	LOAD r7, @x",
            "	LOAD r6, @i",
            "	ADD r7, r7, r6",
            "	STORE @x, r7",
            "	JMP Lab2",
            "Lab3	LOAD r7, @x",
            "	PRINT r7",
            "	HALT",
        ])
        self.assertEqual(asm, good)

    def test2(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor16Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        asm = engine.getAsm(actionsList, True)
        good = "\n".join([
            "	MOVE r7, #0",
            "	STORE @x, r7",
            "	MOVE r7, #0",
            "	STORE @i, r7",
            "Lab2	LOAD r7, @i",
            "	MOVE r6, #10",
            "	CMP r7, r6",
            "	BLT Lab1",
            "	JMP Lab3",
            "Lab1	LOAD r7, @i",
            "	ADD r7, r7, #1",
            "	STORE @i, r7",
            "	LOAD r7, @x",
            "	LOAD r6, @i",
            "	ADD r7, r7, r6",
            "	STORE @x, r7",
            "	JMP Lab2",
            "Lab3	LOAD r7, @x",
            "	PRINT r7",
            "	HALT",
            "@x	0",
            "@i	0"
        ])
        self.assertEqual(asm, good)

    def test3(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor12Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        asm = engine.getAsm(actionsList, True)
        good = "\n".join([
            "	LOAD r3, @#0",
            "	STORE @x, r3",
            "	LOAD r3, @#0",
            "	STORE @i, r3",
            "Lab2	LOAD r3, @i",
            "	LOAD r2, @#10",
            "	CMP r3, r2",
            "	BLT Lab1",
            "	JMP Lab3",
            "Lab1	LOAD r3, @i",
            "	LOAD r2, @#1",
            "	ADD r3, r3, r2",
            "	STORE @i, r3",
            "	LOAD r3, @x",
            "	LOAD r2, @i",
            "	ADD r3, r3, r2",
            "	STORE @x, r3",
            "	JMP Lab2",
            "Lab3	LOAD r3, @x",
            "	PRINT r3",
            "	HALT",
            "@#0	0",
            "@x	0",
            "@i	0",
            "@#10	10",
            "@#1	1"
        ])
        self.assertEqual(asm, good)

class CollectAdressesTest(unittest.TestCase):
    def test1(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor16Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        addressList = engine._getAdresses(actionsList)
        result = "\n".join(sorted([
            "{} : {}".format(it, n) for it, n in addressList.items()
        ]))
        
        good = "\n".join([
            "@i : 21",
            "@x : 20",
            "Lab1 : 4",
            "Lab2 : 9",
            "Lab3 : 17"
        ])
        self.assertEqual(result, good)

    def test2(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor12Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        addressList = engine._getAdresses(actionsList)
        result = "\n".join(sorted([
            "{} : {}".format(it, n) for it, n in addressList.items()
        ]))
         
        good = "\n".join([
            "@#0 : 21",
            "@#1 : 25",
            "@#10 : 24",
            "@i : 23",
            "@x : 22",
            "Lab1 : 4",
            "Lab2 : 9",
            "Lab3 : 18"
        ])
        self.assertEqual(result, good)
    
class BinarySingleTest(unittest.TestCase):
    def test1(self):
        engine = Processor12Bits()
        fifo = ActionsFIFO()
        fifo.append(Register(1, False), Register(2, False), Register(0, False), Operators.ADD)
        binaryCode = "\n".join(engine.getBinary([fifo]))
        self.assertEqual(binaryCode, "111110000110")

    def test2(self):
        engine = Processor16Bits()
        fifo = ActionsFIFO()
        fifo.append(Register(1, False), Register(2, False), Register(0, False), Operators.ADD)
        binaryCode = "\n".join(engine.getBinary([fifo]))
        self.assertEqual(binaryCode, "0110000000001010")

    def test3(self):
        engine = Processor16Bits()
        fifo = ActionsFIFO()
        fifo.append(Register(1, False), Litteral(45), Register(5, False), Operators.ADD)
        binaryCode = "\n".join(engine.getBinary([fifo]))
        self.assertEqual(binaryCode, "1000101001101101")


class BinaryCompleteTest(unittest.TestCase):
    maxDiff = None
    def test1(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor16Bits()
        cm = CM(engine, code)
        fifos = cm.compile()
        binaryCode = "\n".join(engine.getBinary(fifos))
        good = "\n".join([
            "0100111100000000",
            "0111000010100111",
            "0100111100000000",
            "0111000010101111",
            "0011111000010101",
            "0100111000001010",
            "0001100000111110",
            "0001010000001001",
            "0000100000010001",
            "0011111000010101",
            "1000111111000001",
            "0111000010101111",
            "0011111000010100",
            "0011110000010101",
            "0110000111111110",
            "0111000010100111",
            "0000100000000100",
            "0011111000010100",
            "0010000000000111",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000"
        ])
        self.assertEqual(binaryCode, good)

    def test2(self):
        textCode = "\n".join([
            "x = 0",
            "i = 0",
            "while i < 10:",
            "    i = i + 1",
            "    x = x + i",
            "print(x)"
        ])
        code = CP.parse(code = textCode)
        engine = Processor12Bits()
        cm = CM(engine, code)
        fifos = cm.compile()
        binaryCode = "\n".join(engine.getBinary(fifos))
        good = "\n".join([
            "100110010101",
            "101001011011",
            "100110010101",
            "101001011111",
            "100110010111",
            "100100011000",
            "111101011110",
            "001100001001",
            "000100010010",
            "100110010111",
            "100100011001",
            "111110001110",
            "101001011111",
            "100110010110",
            "100100010111",
            "111110001110",
            "101001011011",
            "000100000100",
            "100110010110",
            "010000000011",
            "000000000000",
            "000000000000",
            "000000000000",
            "000000000000",
            "000000001010",
            "000000000001"
        ])
        self.assertEqual(binaryCode, good)
