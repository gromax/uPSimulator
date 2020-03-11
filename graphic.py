"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *
from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine


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
            Graphic(textCode, cm16.getAsm())

class TextWidget:
    normalBackground = 'white'
    highlightedBackground = 'orange2'
    cols = 30
    showLineNumber = True
    lineNumberDigits = 3
    lineNumberTab = '   '
    def __init__(self, container, text, **kwargs):

        for key, value in kwargs.items():
            if key == "cols":
                self.cols = value
            elif key == 'shownumbers':
                self.showLineNumber = value
            elif key == 'numbersdigits':
                self.lineNumberDigits = value
            elif key == 'numbertab':
                self.lineNumberTab = value

        textLines = text.split("\n")
        if self.showLineNumber:
            for i in range(len(textLines)):
                textLines[i] = ('{:0'+str(self.lineNumberDigits)+'d}:'+self.lineNumberTab+textLines[i]).format(i)
        if self.cols == 0:
            # on ajuste la taille de la zone de texte au contenu
            # le +2 est un bricolage car une tabulation comptant pour un caractère
            # pourra en occuper 3 dans la zone
            self.cols = max([len(line) for line in textLines]) + 2
        else:
            # on complète avec des espaces pour que la ligne occupe toute la largeur
            for i in range(len(textLines)):
                textLines[i] += " "*(self.cols - len(textLines[i]) % self.cols)

        formatedText = "\n".join(textLines)
        self.__textZone = Text(container, width=self.cols, height=50, bg=self.normalBackground)
        self.__textZone.insert(END, formatedText)
        self.__textZone.config(state=DISABLED)
        self.__textZone.pack(padx=10, pady=10)
        self.highlightLine(0)

        self.__textZone.tag_configure("HIGHLIGHTED", background=self.highlightedBackground, foreground='white')



    def highlightLine(self,n):
        self.__textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')
        self.__textZone.tag_add("HIGHLIGHTED", str(n+1)+".0", str(n+1)+".end")




class Graphic:
    def __init__(self, textCode, asm):
        root = Tk()

        # grille
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)

        # partie programme
        programFrame = LabelFrame(root, width=200, height=200, bd=2, text='Votre code')
        self.__program = TextWidget(programFrame, textCode, numbersdigits=2)
        programFrame.grid(row=0, column=0, sticky="nsew")

        # partie asm
        asmFrame = LabelFrame(root, width=200, height=200, bd=2, text='Assembleur')
        self.__asmCode = TextWidget(asmFrame, str(asm), cols=0, numbertab=' ')
        asmFrame.grid(row=0, column=1, sticky="nsew")

        binaryFrame = LabelFrame(root, width=200, height=200, bd=2, text='Binaire')
        self.__asmBinary = TextWidget(binaryFrame, asm.getBinary(), cols=0, numbertab=' ')
        binaryFrame.grid(row=0, column=2, sticky="nsew")

        self.__root = root

    def show(self):
        self.__root.mainloop()


if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





