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

from modules.compilemanager import CompilationManager as CM
from modules.parser.code import CodeParser as CP

class MyTest(unittest.TestCase):
    def test1(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        l4 = Litteral(4)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, l4, r0, op)

        asm = engine.getAsmCode(actions)
        self.assertEqual(asm, "	ADD r0, r1, #4")

    def test2(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, r0, r0, op)

        asm = engine.getAsmCode(actions)
        self.assertEqual(asm, "	ADD r0, r1, r0")
    
    def test3(self):
        r0 = Register(0, False)
        r1 = Register(1, False)
        l4 = Litteral(4)
        op = Operators.ADD
        engine = Processor16Bits()
        actions = ActionsFIFO()
        actions.append(r1, l4, r0, op, r1, r0, r0, op)

        asm = engine.getAsmCode(actions)
        good = "\n".join([
            "	ADD r0, r1, #4",
            "	ADD r0, r1, r0"
        ])
        self.assertEqual(asm, good)

class AsmTest(unittest.TestCase):
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
        asmList = [engine.getAsmCode(actionItem) for actionItem in actionsList]
        asm = "\n".join(asmList)
        print(asm)
        good = "\n".join([
            "	MOVE r7, #0",
            "	STORE r7, @x",
            "	MOVE r7, #0",
            "	STORE r7, @i",
            "Lab2	LOAD r7, @i",
            "	MOVE r6, #10",
            "	CMP r7, r6",
            "	BLT Lab1",
            "	JMP Lab3",
            "Lab1	LOAD r7, @i",
            "	ADD r7, r7, #1",
            "	STORE r7, @i",
            "	LOAD r7, @x",
            "	LOAD r6, @i",
            "	ADD r7, r7, r6",
            "	STORE r7, @x",
            "	JMP Lab2",
            "Lab3	LOAD r7, @x",
            "	PRINT r7",
            "	HALT"
        ])
        self.assertEqual(asm, good)
