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
        except Exception as e :
            if codeFrame != None:
                codeFrame.writeMessage(e)
            else:
                print(e)
        else :
            if isinstance(codeFrame, InputCodeWidget):
                codeFrame.destroy()
            asm = cm.getAsm()
            self.initSimulationFrame(engine, textCode, cm.getAsm())

    def initSimulationFrame(self, engine, textCode, asm):
        executeur = Executeur(engine,asm.getDecimal())
        simFrame = SimulationWidget(self.__root, executeur, textCode, asm)
        simFrame.pack()

    def show(self):
        self.__root.mainloop()





if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





