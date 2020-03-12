"""
.. module:: widgets
   :synopsis: objets constitant l'interface graphique
"""

from tkinter import *

class TextWidget:
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    HL_COLOR = 'white'
    MIN_TAB_SIZE = 3
    cols = 30
    lineNumberFormat = '{:03d}:   '
    lines = 25
    lineNumberOffset = 0
    def __init__(self, container, text, **kwargs):
        for key, value in kwargs.items():
            if key == "cols":
                self.cols = value
            elif key == 'numbers':
                self.lineNumberFormat = value
            elif key == 'lines':
                self.lines = value
            elif key == 'offset':
                self.lineNumberOffset = value

        textLines = self.formatText(text)
        if self.lineNumberFormat != '':
            for i in range(len(textLines)):
                textLines[i] = (self.lineNumberFormat+textLines[i]).format(i+self.lineNumberOffset)
        if self.cols == 0:
            # on ajuste la taille de la zone de texte au contenu
            self.cols = max([len(line) for line in textLines])

        formatedText = "\n".join(textLines)
        self.__textZone = Text(container, width=self.cols, height=self.lines, bg=self.BACKGROUND)
        self.__textZone.insert(END, formatedText)
        self.__textZone.config(state=DISABLED)
        self.__textZone.pack(padx=10, pady=10)

        self.__textZone.tag_configure("HIGHLIGHTED", background=self.HL_BACKGROUND, foreground=self.HL_COLOR)

    def formatText(self, text):
        # découpage en lignes, recherche d'éventuelles tabulation
        textLines = [ item.split("\t") for item in text.split("\n") ]
        slicesNumber = max([len(item) for item in textLines])
        for indexSlice in range(slicesNumber):
            size = max([len(line[indexSlice]) for line in textLines if len(line)>indexSlice])
            size = max(self.MIN_TAB_SIZE, size)
            print(size)
            for indexLine in range(len(textLines)):
                line = textLines[indexLine]
                if len(line)>indexSlice:
                    l = len(line[indexSlice])
                    line[indexSlice] += " "*(size - l)
                else:
                    line[indexSlice] = " "*size
        print(textLines)
        formatedTextLines = [ " ".join(line) for line in textLines]
        return formatedTextLines

    def highlightLine(self,lineIndex:int):
        self.__textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')
        lineIndex -= self.lineNumberOffset
        if lineIndex != -1:
            tag = str(lineIndex+1)
            self.__textZone.tag_add("HIGHLIGHTED", tag+".0", tag+".end")


class BufferWidget:
    COLS = 10
    BACKGROUND = 'white'
    MAXLENGTH = 3
    def __init__(self, container, executeur):
        self.__executeur = executeur
        label = Label(container,text='Buffer')
        self.__saisie = Text(container, width=self.COLS, height=1, bg=self.BACKGROUND)
        button = Button(container, text='Entrer')
        self.__bufferedText = StringVar()
        self.__buffered = Label(container, textvariable=self.__bufferedText, relief='groove')
        label.pack()
        self.__saisie.pack()
        button.pack()
        self.__buffered.pack()
        button.bind("<Button-1>", self.bufferize)
        self.refresh()

    def bufferize(self, evt):
        text = self.__saisie.get(1.0, 'end').strip()
        try:
            value = int(text)
        except Exception:
            self.__bufferedText.set('Nombre entier attendu !')
        else:
            self.__executeur.bufferize(value)
            self.refresh()

    def refresh(self):
        buff = self.__executeur.getMemories()["buffer"]
        buffStrList = [str(item) for item in buff]
        if len(buffStrList) > self.MAXLENGTH:
            buffStrList = buffStrList[:self.MAXLENGTH] + ["..."]
        self.__bufferedText.set(" ; ".join(buffStrList))




if __name__=="__main__":
    from processorengine import ProcessorEngine
    from executeur import Executeur
    engine16 = ProcessorEngine()
    oExecuteur = Executeur(engine16,[0])
    root = Tk()
    testText = "00011101\n11100110"
    textFrame = TextWidget(root, testText, cols=0)
    buffer = BufferWidget(root, oExecuteur)
    root.mainloop()






