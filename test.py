from assembleurcontainer import *
from expressionparser import ExpressionParser
from processorengine import ProcessorEngine
EP = ExpressionParser()
engine = ProcessorEngine()
cm = AssembleurContainer(engine)
cm.pushMove(2,1)
cm.pushMove(Litteral(2),1)
cm.pushStore(1,Variable('x'))

cm.pushLoad(Variable('x'),3)

cm.getAsmSize()
cm.getMemAbsPos(Variable('x'))

print(str(cm))
print(cm.getBinary())