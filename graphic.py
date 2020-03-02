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

        # partie programme
        programInputFrame = Frame(root, width=200, height=200)
        self.__programInput = Text(programInputFrame, width = 30, height = 10, bg = 'white')
        self.__programInput.pack(padx=10, pady=10)
        self.__programInput.insert('1.0', 'here is my text to insert')
        self.__programInput.bind('<Double-Button-1>', self.clear_programInput)
        self.__errorMessage = Text(programInputFrame, width = 30, height = 10, bg = 'white')
        self.__errorMessage.pack(padx=10, pady=10)
        compileButton = Button(programInputFrame, text='Compile', command=self.doCompile)
        compileButton.pack()

        programInputFrame.grid(row=0, column=0, sticky="nsew")


        # partie asm
        asmFrame = Frame(root, width=200, height=200)
        self.__asmCode = Text(asmFrame, width = 30, height = 20, bg = 'white')
        self.__asmCode.pack(padx=10, pady=10,side = RIGHT)
        self.__asmBinary = Text(asmFrame, width = 30, height = 20, bg = 'white')
        self.__asmBinary.pack(padx=10, pady=10, side = RIGHT)
        asmFrame.grid(row=0, column=1, sticky="nsew")

        self.__root = root

    def show(self):
        self.__root.mainloop()

    def clear_programInput(self,event):
        self.__programInput.delete('1.0', 'end')

    def doCompile(self):
        self.__errorMessage.delete('1.0', 'end')
        engine16 = ProcessorEngine()
        text_code = self.__programInput.get(1.0, 'end')
        try :
            cp = CodeParser(code = text_code)
            structuredList = cp.getFinalStructuredList()
            cm16 = CompilationManager(engine16, structuredList)
        except Exception as e :
            self.__errorMessage.insert('1.0',e)
        else :
            self.__asmCode.insert('1.0',cm16.getAsm())
            self.__asmBinary.insert('1.0',cm16.getAsm().getBinary())

if __name__=="__main__":
    g = Graphic()
    g.show()





