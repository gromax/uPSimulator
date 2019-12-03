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
expr = EP.buildExpression('3*x+2')
condition = EP.buildExpression('3*x+2<4')

elIf = IfElement(8, condition)
str(elIf)