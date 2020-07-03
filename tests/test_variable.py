"""
.. module:: tests.test_variable
:synopsis: Test du module variables
"""


import unittest

from modules.primitives.variable import Variable

class MyTest(unittest.TestCase):
    def test(self):
        v = Variable("x")
        self.assertEqual(v.value, 0)
