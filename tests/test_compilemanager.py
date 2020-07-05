"""
.. module:: tests.test_compilemanager
:synopsis: Test du module compilemanager
"""


import unittest

class MyTest(unittest.TestCase):
    def test1(self):
        self.assertEqual(True, False)


"""
    from modules.parser.expression import ExpressionParser as EP
    from processor16bits import Processor16Bits
    from primitives.variable import Variable
    from structuresnodes import WhileNode
    from modules.parser.code import CodeParser

    engine = Processor16Bits()

    varX = Variable('x')
    varY = Variable('y')

    affectationX = AffectationNode(4, varX, EP.buildExpression('-3*x+1')) # mypy: ignore
    affectationY = AffectationNode(5, varY, EP.buildExpression('y+x')) # mypy: ignore
    structuredList = [
        AffectationNode(1, varX, EP.buildExpression('0')),
        AffectationNode(2, varY, EP.buildExpression('0')),
        WhileNode(3, EP.buildExpression('x < 10 or y < 100'), [affectationX, affectationY]),
        PrintNode(6, EP.buildExpression('y'))
    ]

    cm = CompilationManager(engine, structuredList)
    print(cm.asm)
    print()
    print(cm.asm.getBinary())

    print()
    print()
    code = CodeParser.parse(filename = "example2.code")
    cm = CompilationManager(engine, code)
    print(cm.asm)
"""