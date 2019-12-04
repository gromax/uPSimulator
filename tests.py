from expressionParser import *
from errors import *

EP = ExpressionParser()

for strExpression in [
  "3x+ 5 -y",
  "3*x+ 5 -y",
  "+ 6 -4*x / 3",
  "x<4 and y>3*x",
  "(2 < 4) * (3+x)",
  "(2+x) and (x-1)"
]:
    try:
        print("Test de :",strExpression)
        oExpression = EP.buildExpression(strExpression)
        print(oExpression) # Utilise la conversion to string de Expression
        print(oExpression.getType()) # affichage du type, 'bool' 'int' ou None
    except ExpressionError as e:
        print(e)
    except Exception as e:
        print("Erreur inattendue :",e)
    else:
        print("Tout s'est bien passé'")
    print()
    print("------------")
    print()


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
  { 'type':'while', 'lineNumber':3, 'condition':EP.buildExpression('x < 10'), 'children':[
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