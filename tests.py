from expressionparser import *
from errors import *

'''
Tests pour les structures
'''

from structureelements import *

VM = VariableManager()
EP = ExpressionParser(VM)

varX = VM.addVariableByName('x')
varY = VM.addVariableByName('y')
expr = EP.buildExpression('3*x+2')
condition = EP.buildExpression('3*x+2<4')

listeObjetsParsed = [
  { 'type':'affectation', 'lineNumber':1, 'variable': varX, 'expression': EP.buildExpression('0') },
  { 'type':'affectation', 'lineNumber':2, 'variable': varY, 'expression': EP.buildExpression('0') },
  { 'type':'while', 'lineNumber':3, 'condition':EP.buildExpression('x < 10 or y < 100'), 'children':[
    { 'type':'affectation', 'lineNumber':4, 'variable': varX, 'expression': EP.buildExpression('x + 1') },
    { 'type':'affectation', 'lineNumber':5, 'variable': varY, 'expression': EP.buildExpression('y + x') }
  ]},
  { 'type':'print', 'lineNumber':6, 'expression': EP.buildExpression('y') }


]


c = Container()
c.append(listeObjetsParsed)
print(c)
print()
print("Version linéarisée :")
print()
lC = c.getLinearized()
print(lC)
