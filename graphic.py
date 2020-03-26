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

class InputCodeWindow:
    def __init__(self):
        root = Tk()
        root.title('Simulation de processeur')

        programInputFrame = LabelFrame(root, width=200, height=200, bd=2, text='Votre code')
        self.__programInput = Text(programInputFrame, width = 30, height = 10, bg = 'white')
        self.__programInput.pack(padx=10, pady=10)
        #self.__programInput.insert('1.0', 'here is my text to insert')
        self.__programInput.bind('<Double-Button-1>', self.__clear_programInput)
        compileButton = Button(programInputFrame, text='Compile', command = self.__doCompile)
        compileButton.pack()

        self.__errorMessage = StringVar()
        self.__errorMessage.set("Aucun message...")
        self.__errorMessageFrame = Message(programInputFrame, width = 300, textvariable=self.__errorMessage, bg = '#faa', relief='groove')
        self.__errorMessageFrame.pack(padx=10, pady=10)

        programInputFrame.pack()
        self.__root = root

    def show(self):
        self.__root.mainloop()

    def __clear_programInput(self,event):
        self.__programInput.delete('1.0', 'end')

    def __doCompile(self):
        self.__errorMessage.set("Compilation...")
        engine16 = ProcessorEngine()
        textCode = self.__programInput.get(1.0, 'end')
        try :
            cp = CodeParser(code = textCode)
            structuredList = cp.getFinalStructuredList()
            cm16 = CompilationManager(engine16, structuredList)
        except Exception as e :
            self.__errorMessage.set(e)
        else :
            self.__errorMessage.set("Compilation effectuée !")
            Graphic(engine16, textCode, cm16.getAsm())

class Graphic:
    def __init__(self, engine, textCode, asm):
        root = Tk()
        self.engine = engine
        self.asm = asm
        # grille
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=3)

        # partie programme
        self.__program = TextWidget(root, textCode, numbersdigits=2, lines=20, offset=1, name="Votre code")
        self.__program.grid(row=0, column=0)

        self.__stepButton = Button(self.__program, width=20, height=1, text='Pas')
        self.__stepButton.pack()

        self.__stepButton.bind('<Button-1>', self.stepRun)

        # partie asm
        self.__asmFrame = TextWidget(root, str(asm), cols=0, numbertab=' ', name='Assembleur')
        self.__asmFrame.grid(row=0, column=1)

        self.__root = root

        self.executeur = Executeur(engine,asm.getDecimal())
        ualW = UalWidget(root, self.executeur.ual)
        inputBufferW = BufferWidget(root, self.executeur.inputBuffer)
        instrRegW = RegisterWidget(root, self.executeur.instructionRegister, unsigned = True)
        linePointerW = RegisterWidget(root, self.executeur.linePointer, unsigned = True)
        memoryW = MemoryWidget(root, self.executeur.memory)
        screenW = ScreenWidget(root, self.executeur.screen)

        inputBufferW.grid(row=0, column=2)
        screenW.grid(row=1, column=2)

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



if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





