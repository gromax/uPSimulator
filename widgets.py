"""
.. module:: widgets
   :synopsis: objets constitant l'interface graphique
"""

from tkinter import *
from executeurcomponents import Buffer, Screen

class TextWidget(Frame):
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    HL_COLOR = 'white'
    MIN_TAB_SIZE = 3
    cols = 30
    lineNumberFormat = '{:03d}:   '
    lines = 25
    lineNumberOffset = 0
    def __init__(self, parent, text, **kwargs):
        Frame.__init__(self, parent, class_='TextWidget')

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
        self.__textZone = Text(self, width=self.cols, height=self.lines, bg=self.BACKGROUND)
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


class BufferWidget(Frame):
    SAISIE_COLS = 10
    BACKGROUND = 'white'
    MAX_BUFFER_LENGTH = 30
    def __init__(self, parent, buffer):
        Frame.__init__(self, parent, class_='BufferWidget')
        self.__buffer = buffer
        buffer.bind("onread", self.onreadwrite)
        buffer.bind("onwrite", self.onreadwrite)
        # message en entête
        self.__messageText = StringVar()
        self.__messageText.set("Saisie")
        label = Label(self,textvariable=self.__messageText)
        label.grid(row=0, column=0, columnspan=2)
        # champ de saisie
        self.__saisie = Text(self, width=self.SAISIE_COLS, height=1, bg=self.BACKGROUND)
        self.__saisie.grid(row=1, column=0)
        # bouton de validation
        button = Button(self, text='Entrer')
        button.grid(row=1, column=1)
        # contenu du buffer
        self.__bufferedText = StringVar()
        buffered = Label(self, textvariable=self.__bufferedText, relief='groove')
        buffered.grid(row=2, column=0, columnspan=2)
        button.bind("<Button-1>", self.bufferize)
        self.refreshStrBuffer()

    def bufferize(self, evt):
        text = self.__saisie.get(1.0, 'end').strip()
        try:
            value = int(text)
        except Exception:
            self.__messageText.set('Nombre entier attendu !')
            self.after(1000, self.refresh)
        else:
            self.__buffer.write(value)

    def onreadwrite(self, params):
        self.__messageText.set("Saisie")
        self.refreshStrBuffer()
        self.refresh()

    def onreadempty(self, params):
        self.__messageText.set("Saisie en attente")

    def refreshStrBuffer(self):
        buffStr = " ; ".join([str(item) for item in self.__buffer.list])
        if len(buffStr) == 0:
            buffStr = "Buffer vide"
        elif len(buffStr) > self.MAX_BUFFER_LENGTH:
            buffStr = buffStr[:self.MAX_BUFFER_LENGTH]+"..."
        self.__bufferedText.set(buffStr)


class ScreenWidget(Frame):
    SCREEN_COLS = 10
    SCREEN_LINES = 5
    BACKGROUND = 'white'

    def __init__(self, parent, screen):
        self.__screen = screen
        screen.bind("onclear", self.onclear)
        screen.bind("onwrite", self.onwrite)
        Frame.__init__(self, parent, class_='PrintWidget')
        # message en entête
        label = Label(self,text="Écran")
        label.grid(row=0, column=0)
        # bouton d'effacement
        button = Button(self, text='Effacer')
        button.grid(row=0, column=1)
        button.bind("<Button-1>", self.clearScreen)
        # affichage
        self.__textZone = Text(self, width=self.SCREEN_COLS, height=self.SCREEN_LINES, bg=self.BACKGROUND)
        self.__textZone.grid(row=1, column=0, columnspan=2)
        self.__textZone.config(state=DISABLED)

    def clearScreen(self, evt):
        self.__screen.clear()

    def onclear(self, params):
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        self.__textZone.config(state=DISABLED)


    def onwrite(self, params):
        if "writed" in params:
            value = str(params["writed"])
            self.__textZone.config(state=NORMAL)
            self.__textZone.insert('end', value+"\n")
            self.__textZone.config(state=DISABLED)

if __name__=="__main__":
    root = Tk()
    testText = "00011101\n11100110"
    textFrame = TextWidget(root, testText, cols=0)
    saisie = BufferWidget(root, Buffer())
    sw = Screen()
    screen = ScreenWidget(root, sw)
    sw.write(4)
    sw.write(45)
    textFrame.pack()
    saisie.pack()
    screen.pack()


    root.mainloop()






