"""
.. module:: tests.test_cem
:synopsis: Test du module compileexpressionmanager
"""

from modules.engine.processor12bits import Processor12Bits
from modules.engine.processor16bits import Processor16Bits
from modules.parser.expression import ExpressionParser
from modules.compileexpressionmanager import CompileExpressionManager
from modules.primitives.register import RegistersManager

import unittest

class LineTest(unittest.TestCase):
    def test1(self):
        strExpression = "5*(2*x+4)-x*y"
        engine = Processor12Bits()
        regManager = RegistersManager(engine.registersNumber())
        cem = CompileExpressionManager(engine, regManager)

        parsed = ExpressionParser.buildExpression(strExpression)
        fifo = parsed.getFIFO(engine.litteralDomain)
        
        
        actions = cem.compile(fifo)
        
        good = "\n".join([
            "	@x r3 load",
            "	@#2 r2 load",
            "	r3 r2 r3 *",
            "	@#4 r2 load",
            "	r3 r2 r3 +",
            "	@#5 r2 load",
            "	r3 r2 r3 *",
            "	@x r2 load",
            "	@y r1 load",
            "	r2 r1 r2 *",
            "	r3 r2 r3 -"
        ])
        
        self.assertEqual(str(actions), good)

    def test2(self):
        strExpression = "5*(2*x+4)-x*y"
        engine = Processor16Bits()
        regManager = RegistersManager(engine.registersNumber())
        cem = CompileExpressionManager(engine, regManager)

        parsed = ExpressionParser.buildExpression(strExpression)
        fifo = parsed.getFIFO(engine.litteralDomain)
       
        actions = cem.compile(fifo)
        
        good = "\n".join([
            "	@x r7 load",
            "	@y r6 load",
            "	r7 r6 r7 *",
            "	@x r6 load",
            "	r6 #2 r6 *",
            "	r6 #4 r6 +",
            "	r6 #5 r6 *",
            "	r6 r7 r7 -"
        ])
        
        self.assertEqual(str(actions), good)

    def test3(self):
        strExpression = "(((2+4)*(4+1)) - ((2+4)*(4+1))) * (((2+4)*(4+1)) - ((2+4)*(4+1)))"
        engine = Processor12Bits()
        regManager = RegistersManager(engine.registersNumber())

        cem = CompileExpressionManager(engine, regManager)
        parsed = ExpressionParser.buildExpression(strExpression)
        fifo = parsed.getFIFO(engine.litteralDomain)
        actions = cem.compile(fifo)
        
        good = "\n".join([
            "	@#4 r3 load",
            "	@#2 r2 load",
            "	r3 r2 r3 +",
            "	@#4 r2 load",
            "	@#1 r1 load",
            "	r2 r1 r2 +",
            "	r3 r2 r3 *",
            "	@#4 r2 load",
            "	@#2 r1 load",
            "	r2 r1 r2 +",
            "	@#4 r1 load",
            "	@#1 r0 load",
            "	r1 r0 r1 +",
            "	r2 r1 r2 *",
            "	r3 r2 r3 -",
            "	@#4 r2 load",
            "	@#2 r1 load",
            "	r2 r1 r2 +",
            "	@#4 r1 load",
            "	@#1 r0 load",
            "	r1 r0 r1 +",
            "	r2 r1 r2 *",
            "	@#4 r1 load",
            "	@#2 r0 load",
            "	r1 r0 r1 +",
            "	@#4 r0 load",
            "	r3 _m0 store",
            "	r0 r3 move",
            "	@#1 r0 load",
            "	r3 r0 r3 +",
            "	r1 r3 r3 *",
            "	r2 r3 r3 -",
            "	_m0 r2 load",
            "	r2 r3 r3 *"
        ])
        
        self.assertEqual(str(actions), good)

    def test4(self):
        strExpression = "3*x > 4"
        engine = Processor16Bits()
        regManager = RegistersManager(engine.registersNumber())

        cem = CompileExpressionManager(engine, regManager)
        parsed = ExpressionParser.buildExpression(strExpression)
        fifo = parsed.getFIFO(engine.litteralDomain)
        actions = cem.compile(fifo)
        
        good = "\n".join([
            "	@x r7 load",
            "	r7 #3 r7 *",
            "	#4 r6 move",
            "	r7 r6 >"
        ])
        
        self.assertEqual(str(actions), good)

   
