"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *
from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine

class Graphic:
    def __init__(self):
        root = Tk()

        # grille
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)

        # partie programme
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

        programInputFrame.grid(row=0, column=0, sticky="nsew")


        # partie asm
        asmFrame = LabelFrame(root, width=200, height=200, bd=2, text='Assembleur')
        self.__asmCode = Text(asmFrame, width = 30, height = 20, bg = 'white')
        self.__asmCode.pack(padx=10, pady=10,side = RIGHT)
        asmFrame.grid(row=0, column=1, sticky="nsew")

        binaryFrame = LabelFrame(root, width=200, height=200, bd=2, text='Binaire')
        self.__asmBinary = Text(binaryFrame, width = 30, height = 20, bg = 'white')
        self.__asmBinary.pack(padx=10, pady=10, side = RIGHT)
        binaryFrame.grid(row=0, column=2, sticky="nsew")

        self.__root = root

    def show(self):
        self.__root.mainloop()

    def __clear_programInput(self,event):
        self.__programInput.delete('1.0', 'end')

    def __doCompile(self):
        self.__errorMessage.set("Compilation...")
        self.__asmCode.delete('1.0', 'end')
        self.__asmBinary.delete('1.0', 'end')
        engine16 = ProcessorEngine()
        text_code = self.__programInput.get(1.0, 'end')
        try :
            cp = CodeParser(code = text_code)
            structuredList = cp.getFinalStructuredList()
            cm16 = CompilationManager(engine16, structuredList)
        except Exception as e :
            self.__errorMessage.set(e)
        else :
            self.__errorMessage.set("Compilation effectuée !")
            self.__asmCode.insert('1.0',cm16.getAsm())
            self.__asmBinary.insert('1.0',cm16.getAsm().getBinary())

if __name__=="__main__":
    g = Graphic()
    g.show()





