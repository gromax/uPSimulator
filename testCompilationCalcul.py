#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:58:15 2019

@author: desjouis_brufau
"""
from expressionparser import *
from errors import *
from expression import *
from expressionconvert import *

EP = ExpressionParser()

strtest2= ' 3*17+9-(4+1)*(2+3) '

monExpression = EP.buildExpression(strtest2)

CV = CompileExpressionManager()
CV.compileExpression(monExpression)
