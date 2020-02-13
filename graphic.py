"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *

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
        self.__errorMessage = Text(programInputFrame, width = 30, height = 10, bg = 'white')
        self.__errorMessage.pack(padx=10, pady=10)
        compileButton = Button(programInputFrame, text='Compile', command=self.doCompile)
        compileButton.pack()

        programInputFrame.grid(row=0, column=0, sticky="nsew")


        # partie asm
        asmFrame = Frame(root, width=200, height=200)
        self.__asmCode = Text(asmFrame, width = 30, height = 20, bg = 'white')
        self.__asmCode.pack(padx=10, pady=10)

        asmFrame.grid(row=0, column=1, sticky="nsew")

        self.__root = root

    def show(self):
        self.__root.mainloop()

    def doCompile(self):
        pass


if __name__=="__main__":
    g = Graphic()
    g.show()





