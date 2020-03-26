"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *
from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine
from executeur import Executeur
from widgets import TextWidget, RegisterWidget, ScreenWidget, MemoryWidget, BufferWidget, UalWidget


class InputCodeWidget(LabelFrame):
    def __init__(self, parent):
        self.__parent = parent
        LabelFrame.__init__(self, parent, class_='InputCodeWidget', text='Votre code')
        self.__programInput = Text(self, width = 30, height = 10, bg = 'white')
        self.__programInput.pack(padx=10, pady=10)
        #self.__programInput.insert('1.0', 'here is my text to insert')
        self.__programInput.bind('<Double-Button-1>', self.__clear_programInput)
        compileButton = Button(self, text='Compile', command = self.__doCompile)
        compileButton.pack()

        self.__errorMessage = StringVar()
        self.__errorMessage.set("Aucun message...")
        self.__errorMessageFrame = Message(self, width = 300, textvariable=self.__errorMessage, bg = '#faa', relief='groove')
        self.__errorMessageFrame.pack(padx=10, pady=10)

    def __clear_programInput(self,event):
        self.__programInput.delete('1.0', 'end')

    def __doCompile(self):
        self.__errorMessage.set("Compilation...")
        engine = ProcessorEngine()
        textCode = self.__programInput.get(1.0, 'end')
        try :
            cp = CodeParser(code = textCode)
            structuredList = cp.getFinalStructuredList()
            cm = CompilationManager(engine, structuredList)
        except Exception as e :
            self.__errorMessage.set(e)
        else :
            simulationFrame = SimulationWidget(self.__parent, engine, textCode, cm.getAsm())
            simulationFrame.pack()
            self.destroy()


class SimulationWidget(Frame):
    def __init__(self, parent, engine, textCode, asm):
        Frame.__init__(self, parent, class_='SimulationWidget')
        self.engine = engine
        self.asm = asm
        # grille
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)

        # partie programme
        self.__program = TextWidget(self, textCode, numbersdigits=2, lines=20, offset=1, name="Votre code")
        self.__program.grid(row=0, column=0)

        self.__stepButton = Button(self.__program, width=20, height=1, text='Pas')
        self.__stepButton.pack()

        self.__stepButton.bind('<Button-1>', self.stepRun)

        # partie asm
        self.__asmFrame = TextWidget(self, str(asm), cols=0, numbertab=' ', name='Assembleur')
        self.__asmFrame.grid(row=0, column=1)


        self.executeur = Executeur(engine,asm.getDecimal())
        ualW = UalWidget(self, self.executeur.ual)
        inputBufferW = BufferWidget(self, self.executeur.inputBuffer)
        instrRegW = RegisterWidget(self, self.executeur.instructionRegister, unsigned = True)
        linePointerW = RegisterWidget(self, self.executeur.linePointer, unsigned = True)
        memoryW = MemoryWidget(self, self.executeur.memory)
        screenW = ScreenWidget(self, self.executeur.screen)

        inputBufferW.grid(row=0, column=2)
        screenW.grid(row=1, column=2)
        instrRegW.grid(row=2, column=2)
        memoryW.grid(row=0, column=3)

        self.highlightCodeLine(0)

    def highlightCodeLine(self, memoryLine:int) -> int:
        '''pour un numéro de ligne en mémoire, retourne le numéro
        de la ligne correspondante dans le programme d'origine
        '''
        indexCodeLine = self.asm.getLineNumber(memoryLine)
        self.__asmFrame.highlightLine(memoryLine)
        self.__program.highlightLine(indexCodeLine)

    def show(self):
        self.__root.mainloop()

    def stepRun(self, evt):
        self.executeur.step()
        currentLineIndex = self.executeur.linePointer.intValue
        self.highlightCodeLine(currentLineIndex)




class InputCodeWindow:
    __inputCodeFrame = None
    __simulationFrame = None
    def __init__(self):
        root = Tk()
        root.title('Simulation de processeur')
        self.__root = root
        inputCodeFrame = InputCodeWidget(root)
        inputCodeFrame.pack()

    def show(self):
        self.__root.mainloop()




if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





