"""
.. module:: widgets
   :synopsis: objets constitant l'interface graphique
"""

from tkinter import *
from executeurcomponents import BufferComponent, ScreenComponent, RegisterGroup

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

class MemoryWidget(LabelFrame):
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    HL_COLOR = 'white'
    MODES = {"bin":2, "hex":16, "dec":10}
    cols = 30
    lineNumberFormat = '{:03d}:   '
    lines = 25
    name = "mémoire"
    __mode = "bin"
    __base = 2
    __showModeButton = True
    def __init__(self, parent, memory, **kwargs):

        for key, value in kwargs.items():
            if key == "cols":
                self.cols = value
            elif key == 'numbers':
                self.lineNumberFormat = value
            elif key == 'lines':
                self.lines = value
            elif key == 'name':
                self.name = value
            elif key == 'mode' and value in self.MODES.keys():
                self.__mode = value
            elif key == 'modebutton':
                self.__showModeButton = (value == True)

        LabelFrame.__init__(self, parent, class_='MemoryWidget', text=self.name)
        self.__textZone = Text(self, width=self.cols, height=self.lines, bg=self.BACKGROUND)
        self.__memory = memory
        self.__memory.bind("onwrite", self.onwrite)

        self.__textZone.grid(row = 0, column = 0)
        self.__textZone.tag_configure("HIGHLIGHTED", background=self.HL_BACKGROUND, foreground=self.HL_COLOR)

        # bouton de mode
        if self.__showModeButton:
            self.__modeText = StringVar()
            self.__modeText.set(self.__mode)
            buttonMode = Button(self, textvariable=self.__modeText)
            buttonMode.grid(row=1, column=0)
            buttonMode.bind("<Button-1>", self.switchMode)

        self.selectMode(self.__mode)


    def selectMode(self, mode):
        if mode in self.MODES:
            self.__base = self.MODES[mode]
            self.__mode = mode
            if self.__showModeButton:
                self.__modeText.set(self.__mode)
            self.refresh()

    def switchMode(self, evt):
        modes = list(self.MODES.keys())
        index = (modes.index(self.__mode) + 1) % len(modes)
        self.selectMode(modes[index])

    def highlightLine(self, index:int):
        self.__textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')
        lineTag = index + 1
        self.__textZone.tag_add("HIGHLIGHTED", "{}.0".format(lineTag), "{}.end".format(lineTag))

    def writeValueInLine(self, value, index):
        line = (self.lineNumberFormat + value.toStr(self.__base)).format(index)
        lineTag = index + 1
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('{}.0'.format(lineTag), '{}.end'.format(lineTag))
        self.__textZone.insert('{}.0'.format(lineTag), line)
        self.__textZone.config(state=DISABLED)

    def refresh(self):
        values = self.__memory.content
        lines = [(self.lineNumberFormat+item.toStr(self.__base)).format(index) for index, item in enumerate(values)]
        text = "\n".join(lines)
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        self.__textZone.insert(END, text)
        self.__textZone.config(state=DISABLED)


    def onwrite(self, params):
        if ("writed" in params) and ("index" in params):
            value = params["writed"]
            index = params["index"]
            self.writeValueInLine(value, index)


class BufferWidget(LabelFrame):
    SAISIE_COLS = 10
    BACKGROUND = 'white'
    MAX_BUFFER_LENGTH = 30
    def __init__(self, parent, buffer):
        LabelFrame.__init__(self, parent, class_='BufferWidget', text="Saisie")
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
            if len(text)>2 and text[:2]=='0b':
                value = int(text[2:],2)
            elif len(text)>2 and text[:2]=='0x':
                value = int(text[2:],16)
            else:
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


class ScreenWidget(LabelFrame):
    SCREEN_COLS = 10
    SCREEN_LINES = 5
    BACKGROUND = 'white'
    MODES = {"bin":2, "hex":16, "dec":10}
    __base = 2
    __mode = "bin"

    def __init__(self, parent, screen, **options):
        if "mode" in options:
            self.selectMode(options["mode"])
        self.__screen = screen
        screen.bind("onclear", self.onclear)
        screen.bind("onwrite", self.onwrite)
        LabelFrame.__init__(self, parent, class_='PrintWidget', text="Écran")
        # bouton de mode
        self.__modeText = StringVar()
        self.__modeText.set(self.__mode)
        buttonMode = Button(self, textvariable=self.__modeText)
        buttonMode.grid(row=0, column=0)
        buttonMode.bind("<Button-1>", self.switchMode)

        # bouton d'effacement
        button = Button(self, text='Effacer')
        button.grid(row=0, column=1)
        button.bind("<Button-1>", self.clearScreen)
        # affichage
        self.__textZone = Text(self, width=self.SCREEN_COLS, height=self.SCREEN_LINES, bg=self.BACKGROUND)
        self.__textZone.grid(row=1, column=0, columnspan=2)
        self.__textZone.config(state=DISABLED)

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__base = self.MODES[mode]
            self.__mode = mode
            self.__modeText.set(self.__mode)
            self.refresh()

    def switchMode(self, evt):
        modes = list(self.MODES.keys())
        index = (modes.index(self.__mode) + 1) % len(modes)
        self.selectMode(modes[index])

    def clearScreen(self, evt):
        self.__screen.clear()

    def onclear(self, params):
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        self.__textZone.config(state=DISABLED)

    def onwrite(self, params):
        if "writed" in params:
            strValue = params["writed"].toStr(self.__base)
            self.addLine(strValue)

    def addLine(self, line):
        self.__textZone.config(state=NORMAL)
        self.__textZone.insert('end', line+"\n")
        self.__textZone.config(state=DISABLED)

    def refresh(self):
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        for strItem in self.__screen.getStringList(self.__base):
            self.addLine(strItem)
        self.__textZone.config(state=DISABLED)




if __name__=="__main__":
    root = Tk()
    '''
    testText = "00011101\n11100110"
    textFrame = TextWidget(root, testText, cols=0)
    saisie = BufferWidget(root, BufferComponent(8))
    sc = ScreenComponent(8)
    screen = ScreenWidget(root, sc)
    sc.write(4)
    sc.write(45)
    textFrame.pack()
    saisie.pack()
    screen.pack()
    '''
    rg = RegisterGroup(4, 8, [4, 117, 25, 33])
    rgWidget = MemoryWidget(root, rg, name="Registres")
    rgWidget.pack()
    rg.write(1,15)
    rgWidget.highlightLine(2)
    root.mainloop()






