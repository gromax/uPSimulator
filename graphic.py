"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *
from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine
from executeur import Executeur
from widgets import InputCodeWidget, SimulationWidget
from errors import *

class InputCodeWindow:
    __inputCodeFrame = None
    __simulationFrame = None
    def __init__(self):
        root = Tk()
        root.title('Simulation de processeur')
        self.__root = root
        inputCodeFrame = InputCodeWidget(root, self.doCompile)
        inputCodeFrame.pack()

    def doCompile(self, textCode, codeFrame = None):
        engine = ProcessorEngine()
        try :
            cp = CodeParser(code = textCode)
            structuredList = cp.getFinalStructuredList()
            cm = CompilationManager(engine, structuredList)
            asm = cm.getAsm()
            asm.removeEmptyLines()
            executeur = Executeur(engine,asm.getDecimal())
        except (ExpressionError, CompilationError, ParseError, AttributesError) as e :
            if "lineNumber" in e.errors:
                errorMessage = "[{}] {}".format(e.errors["lineNumber"], e)
            else :
                errorMessage = str(e)
            if codeFrame != None:
                codeFrame.writeMessage(errorMessage)
                if "lineNumber" in e.errors:
                    codeFrame.highlightLine(e.errors["lineNumber"])
            else:
                print(errorMessage)
        except Exception as e:
            if codeFrame != None:
                codeFrame.writeMessage(e)
            else:
                print(e)
        else :
            if isinstance(codeFrame, InputCodeWidget):
                codeFrame.destroy()
            simFrame = SimulationWidget(self.__root, executeur, textCode, asm)
            simFrame.pack()

    def show(self):
        self.__root.mainloop()





if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





