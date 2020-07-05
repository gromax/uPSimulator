"""
.. module:: tests.test_codeparser
:synopsis: Test du module parser.code
"""

from modules.parser.code import CodeParser
from modules.errors import ParseError

import unittest

class LinesTest(unittest.TestCase):
    def test1(self):
        line = '    while ( x < y) : #comment'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_4 >> while (@x < @y)')
    
    def test2(self):
        line = 'if (A==B):'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> if (@A == @B)')
    
    def test3(self):
        line = 'print(x)  #comment'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> print @x')

    def test4(self):
        line = 'A = 15'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> @A = #15')

    def test5(self):
        line = 'A = A + 1  #comment'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> @A = (@A + #1)')

    def test6(self):
        line = 'variable = input()'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> @variable = input()')

    def test7(self):
        line = '    x=x+1'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_4 >> @x = (@x + #1)')

    def test8(self):
        line = 'if x < 10 or y < 100:'
        retour = CodeParser._parseLine(line, 15)
        self.assertEqual(str(retour), '#15_0 >> if ((@x < #10) or (@y < #100))')


class CodesTest(unittest.TestCase):
    def test1(self):
        code = "\n".join([
            "x = 0",
            "if x > 0:",
            "    x = x - 1",
            "elif x == 0 :",
            "    x = x + 1"
        ])

        good = "\n".join([
            "	@x ← #0",
            "	if (@x > #0) {",
            "		@x ← (@x - #1)",
            "	} else {",
            "		if (@x == #0) {",
            "			@x ← (@x + #1)",
            "		}",
            "	}"
        ])

        parsed = CodeParser.parse(code = code)
        strParsed = "\n".join([str(item) for item in parsed])
        self.assertEqual(strParsed, good)

    def test2(self):
        code = "\n".join([
            "x = 0",
            "if x > 0:",
            "    x = x - 1",
            "  print(x)"
        ])
        # erreur d'indentation
        with self.assertRaises(ParseError) as context:
            CodeParser.parse(code = code)
        self.assertTrue("Erreur d'indentation" in str(context.exception))

