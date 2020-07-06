"""
.. module:: tests.test_compilemanager
:synopsis: Test du module compilemanager
"""


import unittest

from modules.primitives.variable import Variable
from modules.structuresnodes import TransfertNode, WhileNode
from modules.parser.expression import ExpressionParser as EP
from modules.engine.processor16bits import Processor16Bits
from modules.compilemanager import CompilationManager as CM
from modules.parser.code import CodeParser as CP

class MyTest(unittest.TestCase):
    def test1(self):
        varX = Variable('x')
        varY = Variable('y')

        affectationX = TransfertNode(4, varX, EP.buildExpression('-3*x+1')) # mypy: ignore
        affectationY = TransfertNode(5, varY, EP.buildExpression('y+x')) # mypy: ignore
        structuredList = [
            TransfertNode(1, varX, EP.buildExpression('0')),
            TransfertNode(2, varY, EP.buildExpression('0')),
            WhileNode(3, EP.buildExpression('x < 10 or y < 100'), [affectationX, affectationY]),
            TransfertNode(6, None, EP.buildExpression('y'))
        ]

        engine = Processor16Bits()
        cm = CM(engine, structuredList)
        actionsList = cm.compile()
        strGlobal = "\n".join([str(item) for item in actionsList])

        good = "\n".join([
            "	#0 r7 move",
            "	r7 @x store",
            "	#0 r7 move",
            "	r7 @y store",
            "Lab2	@x r7 load",
            "	#10 r6 move",
            "	r7 r6 <",
            "	Lab1 goto",
            "	@y r7 load",
            "	#100 r6 move",
            "	r7 r6 <",
            "	Lab1 goto",
            "	Lab3 goto",
            "Lab1	@x r7 load",
            "	r7 #3 r7 *",
            "	r7 r7 -",
            "	r7 #1 r7 +",
            "	r7 @x store",
            "	@y r7 load",
            "	@x r6 load",
            "	r7 r6 r7 +",
            "	r7 @y store",
            "	Lab2 goto",
            "Lab3	@y r7 load",
            "	r7 print",
            "	halt"
        ])
        self.assertEqual(strGlobal, good)

    def test2(self):
        code = CP.parse(filename = "example2.code")
        engine = Processor16Bits()
        cm = CM(engine, code)
        actionsList = cm.compile()
        strGlobal = "\n".join([str(item) for item in actionsList])

        good = "\n".join([
            "	#0 r7 move",
            "	r7 @s store",
            "	#0 r7 move",
            "	r7 @i store",
            "	@m input",
            "Lab2	@i r7 load",
            "	@m r6 load",
            "	r7 r6 <",
            "	Lab1 goto",
            "	Lab3 goto",
            "Lab1	@i r7 load",
            "	r7 #2 r7 %",
            "	#0 r6 move",
            "	r7 r6 ==",
            "	Lab4 goto",
            "	Lab5 goto",
            "Lab4	@s r7 load",
            "	@i r6 load",
            "	r7 r6 r7 +",
            "	r7 @s store",
            "	@s r7 load",
            "	#10 r6 move",
            "	r7 r6 <",
            "	Lab6 goto",
            "	Lab5 goto",
            "Lab6	@s r7 load",
            "	r7 #2 r7 *",
            "	r7 @y store",
            "	@y r7 load",
            "	r7 print",
            "Lab5	@i r7 load",
            "	r7 #3 r7 +",
            "	r7 @i store",
            "	Lab2 goto",
            "Lab3	@s r7 load",
            "	r7 print",
            "	halt"
        ])
        print(strGlobal)
        self.assertEqual(strGlobal, good)