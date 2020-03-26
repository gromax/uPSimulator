"""
.. module:: widgets
   :synopsis: objets constitant l'interface graphique
"""

from tkinter import *
from executeurcomponents import BufferComponent, ScreenComponent, RegisterGroup, MemoryComponent, RegisterComponent, UalComponent

class TextWidget(Frame):
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    HL_COLOR = 'white'
    MIN_TAB_SIZE = 3
    cols = 30
    lineNumberFormat = '{:03d}:   '
    lines = 25
    lineNumberOffset = 0
    __name = "code"
    def __init__(self, parent, text, **kwargs):
        for key, value in kwargs.items():
            if key == "cols":
                self.cols = value
            elif key == 'numbers':
                self.lineNumberFormat = value
            elif key == 'lines':
                self.lines = value
            elif key == 'offset':
                self.lineNumberOffset = value
            elif key == "name":
                self.__name = value
        LabelFrame.__init__(self, parent, class_='TextWidget', text=self.__name)

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
            for indexLine in range(len(textLines)):
                line = textLines[indexLine]
                if len(line)>indexSlice:
                    l = len(line[indexSlice])
                    line[indexSlice] += " "*(size - l)
                else:
                    line[indexSlice] = " "*size
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
    MODES = ("bin", "hex", "dec")
    cols = 30
    lineNumberFormat = '{:03d}:   '
    lines = 25
    __name = "mémoire"
    __mode = "bin"
    __isMemory = False
    def __init__(self, parent, memory, **kwargs):

        for key, value in kwargs.items():
            if key == "cols":
                self.cols = value
            elif key == 'numbers':
                self.lineNumberFormat = value
            elif key == 'lines':
                self.lines = value
            elif key == 'name':
                self.__name = value
            elif key == 'mode' and value in self.MODES.keys():
                self.__mode = value

        LabelFrame.__init__(self, parent, class_='MemoryWidget', text=self.__name)
        self.__textZone = Text(self, width=self.cols, height=self.lines, bg=self.BACKGROUND)
        self.__memory = memory
        self.__memory.bind("onwrite", self.onwrite)
        self.__memory.bind("onread", self.onread)
        self.__memory.bind("onfill", self.onfill)

        self.__textZone.grid(row = 0, column = 0)
        self.__textZone.tag_configure("HIGHLIGHTED", background=self.HL_BACKGROUND, foreground=self.HL_COLOR)

        if isinstance(memory, MemoryComponent):
            # il faut prévoir une adresse
            labelAddressTag = Label(self, text="Adresse")
            labelAddressTag.grid(row=1, column=0)
            self.__isMemory = True
            self.__addressStringVar = StringVar()
            labelAddress = Label(self, textvariable = self.__addressStringVar)
            labelAddress.grid(row=2, column=0)
            self.__memory.bind("onwriteaddress", self.onwriteaddress)

        self.refresh()

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__mode = mode
            self.refresh()

    def highlightLine(self, index:int):
        self.__textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')
        lineTag = index + 1
        self.__textZone.tag_add("HIGHLIGHTED", "{}.0".format(lineTag), "{}.end".format(lineTag))

    def writeValueInLine(self, value, index):
        line = (self.lineNumberFormat + value.toStr(self.__mode)).format(index)
        lineTag = index + 1
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('{}.0'.format(lineTag), '{}.end'.format(lineTag))
        self.__textZone.insert('{}.0'.format(lineTag), line)
        self.__textZone.config(state=DISABLED)
        self.highlightLine(index)

    def writeAddress(self, address):
        intAddress = address.intValue
        if self.__mode == "dec":
            strAddress = self.lineNumberFormat.format(intAddress) + address.toStr("udec")
        else:
            strAddress = self.lineNumberFormat.format(intAddress) + address.toStr(self.__mode)
        self.__addressStringVar.set(strAddress)
        self.highlightLine(intAddress)

    def refresh(self):
        values = self.__memory.content
        lines = [(self.lineNumberFormat+item.toStr(self.__mode)).format(index) for index, item in enumerate(values)]
        text = "\n".join(lines)
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        self.__textZone.insert(END, text)
        self.__textZone.config(state=DISABLED)
        if self.__isMemory:
            self.writeAddress(self.__memory.address)

    def onfill(self, params):
        self.refresh()

    def onread(self, params):
        if "index" in params:
            index = params["index"]
            self.highlightLine(index)

    def onwrite(self, params):
        if ("writed" in params) and ("index" in params):
            value = params["writed"]
            index = params["index"]
            self.writeValueInLine(value, index)

    def onwriteaddress(self, params):
        if ("address" in params) and self.__isMemory:
            self.writeAddress(params["address"])

class BufferWidget(LabelFrame):
    SAISIE_COLS = 10
    BACKGROUND = 'white'
    MAX_BUFFER_LENGTH = 30
    MODES = ("bin", "hex", "dec")
    __mode = "bin"

    def __init__(self, parent, bufferComp):
        LabelFrame.__init__(self, parent, class_='BufferWidget', text="Saisie")
        self.__buffer = bufferComp
        bufferComp.bind("onread", self.onreadwrite)
        bufferComp.bind("onwrite", self.onreadwrite)
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

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__mode = mode
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
            self.after(1000, self.resetMessage)
        else:
            self.__buffer.write(value)

    def resetMessage(self):
        self.__messageText.set('Saisie')

    def onreadwrite(self, params):
        self.__messageText.set("Saisie")
        self.refreshStrBuffer()

    def onreadempty(self, params):
        self.__messageText.set("Saisie en attente")

    def refreshStrBuffer(self):
        buffStr = " ; ".join([item.toStr(self.__mode) for item in self.__buffer.list])
        if len(buffStr) == 0:
            buffStr = "Buffer vide"
        elif len(buffStr) > self.MAX_BUFFER_LENGTH:
            buffStr = buffStr[:self.MAX_BUFFER_LENGTH]+"..."
        self.__bufferedText.set(buffStr)

class ScreenWidget(LabelFrame):
    SCREEN_COLS = 10
    SCREEN_LINES = 5
    BACKGROUND = 'white'
    MODES = ("bin", "hex", "dec")
    __mode = "bin"

    def __init__(self, parent, screen, **options):
        if "mode" in options:
            self.selectMode(options["mode"])
        self.__screen = screen
        screen.bind("onclear", self.onclear)
        screen.bind("onwrite", self.onwrite)
        LabelFrame.__init__(self, parent, class_='PrintWidget', text="Écran")

        # bouton d'effacement
        button = Button(self, text='Effacer')
        button.grid(row=0, column=0)
        button.bind("<Button-1>", self.clearScreen)
        # affichage
        self.__textZone = Text(self, width=self.SCREEN_COLS, height=self.SCREEN_LINES, bg=self.BACKGROUND)
        self.__textZone.grid(row=1, column=0)
        self.__textZone.config(state=DISABLED)
        self.refresh()

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__mode = mode
            self.refresh()

    def clearScreen(self, evt):
        self.__screen.clear()

    def onclear(self, params):
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        self.__textZone.config(state=DISABLED)

    def onwrite(self, params):
        if "writed" in params:
            strValue = params["writed"].toStr(self.__mode)
            self.addLine(strValue)

    def addLine(self, line):
        self.__textZone.config(state=NORMAL)
        self.__textZone.insert('end', line+"\n")
        self.__textZone.config(state=DISABLED)

    def refresh(self):
        self.__textZone.config(state=NORMAL)
        self.__textZone.delete('1.0', 'end')
        for strItem in self.__screen.getStringList(self.__mode):
            self.addLine(strItem)
        self.__textZone.config(state=DISABLED)

class RegisterWidget(LabelFrame):
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    MODES = ("bin", "hex", "dec")
    __unsigned = False
    __mode = 'bin'

    def __init__(self, parent, register, **kwargs):
        for key, value in kwargs.items():
            if key == 'mode' and value in self.MODES.keys():
                self.__mode = value
            elif key == 'unsigned':
                self.__unsigned = (value == True)
        self.__register = register
        register.bind("onwrite", self.onwrite)
        LabelFrame.__init__(self, parent, class_='RegisterWidget', text=register.name)
        self.__valueStringVar = StringVar()
        labelValue = Label(self, textvariable = self.__valueStringVar, bg = self.BACKGROUND)
        labelValue.pack()
        self.refresh()

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__mode = mode
            self.refresh()

    def writeValue(self, value):
        if self.__unsigned and self.__mode == 'dec':
            strValue = value.toStr('udec')
        else:
            strValue = value.toStr(self.__mode)
        self.__valueStringVar.set(strValue)

    def refresh(self):
        self.writeValue(self.__register.read())

    def onwrite(self, params):
        if "writed" in params:
            self.writeValue(params["writed"])

class UalWidget(LabelFrame):
    BACKGROUND = 'white'
    MODES = ("bin", "hex", "dec")
    __mode = 'bin'

    def __init__(self, parent, ual, **kwargs):
        for key, value in kwargs.items():
            if key == 'mode' and value in self.MODES.keys():
                self.__mode = value
        self.__ual = ual
        LabelFrame.__init__(self, parent, class_='RegisterWidget', text="UAL")

        self.__op1StringVar = StringVar()
        self.__op2StringVar = StringVar()
        self.__resultStringVar = StringVar()

        self.__op1StringVar.set("...")
        self.__op2StringVar.set("...")
        self.__resultStringVar.set("...")

        op1Label = Label(self, textvariable = self.__op1StringVar, bg = self.BACKGROUND)
        op2Label = Label(self, textvariable = self.__op2StringVar, bg = self.BACKGROUND)
        resultLabel = Label(self, textvariable = self.__resultStringVar, bg = self.BACKGROUND)

        a = 100
        m = 10
        b = 20
        self.__canvasWidth = 2*m+2*a+b
        self.__canvasHeight = (a+b)//2+2*m
        canvas = Canvas(self, height=self.__canvasHeight, width=self.__canvasWidth)
        self.__canvas = canvas
        p = canvas.create_polygon(m, m, m+a, m, m+a+b/2, m+b/2, m+a+b, m, m+2*a+b, m, m +(a+b)/2+a, m+(a+b)/2, m+(a+b)/2, m+(a+b)/2, fill='', outline='black')
        self.__operationLabel = canvas.create_text(self.__canvasWidth/2, self.__canvasHeight/2, text='...')
        self.__zeroLabel = -1
        self.__posLabel = -1

        op1Label.grid(row=0, column=0)
        op2Label.grid(row=0, column=1)
        canvas.grid(row=1, column=0, columnspan=2)
        resultLabel.grid(row=2, column=0, columnspan=2)

        ual.bind("oncalc", self.oncalc)
        ual.bind("onwriteop1", self.onwriteop1)
        ual.bind("onwriteop2", self.onwriteop2)
        ual.bind("onsetoperation", self.onsetoperation)

    def selectMode(self, mode):
        if mode in self.MODES:
            self.__mode = mode
            self.refresh()

    def onwriteop1(self, params):
        if "writed" in params:
            self.__op1StringVar.set(params["writed"].toStr(self.__mode))

    def onwriteop2(self, params):
        if "writed" in params:
            self.__op2StringVar.set(params["writed"].toStr(self.__mode))

    def oncalc(self, params):
        if "result" in params:
            self.__resultStringVar.set(params["result"].toStr(self.__mode))
        if ("iszero" in params) and params["iszero"] and self.__zeroLabel == -1:
            # création d'un label zéro
            self.__zeroLabel = self.__canvas.create_text(70, 40, text="Zéro", anchor='w', fill='#0A0', font=('Times', 12, 'bold'))
        else:
            # effacement d'un éventuel label
            self.__canvas.delete(self.__zeroLabel)
            self.__zeroLabel = -1
        if ("ispos" in params) and params["ispos"] and self.__posLabel == -1:
            # création d'un label pos
            self.__posLabel = self.__canvas.create_text(70, 60, text="≥ 0", anchor='w', fill='#0A0', font=('Times', 12, 'bold'))
        else:
            # effacement d'un éventuel label
            self.__canvas.delete(self.__posLabel)
            self.__posLabel = -1


    def onsetoperation(self, params):
        if "operation" in params:
            opName = params["operation"]
            self.__canvas.delete(self.__operationLabel)
            self.__operationLabel = self.__canvas.create_text(self.__canvasWidth/2, self.__canvasHeight/2, text=opName, font=('Helvetica', 24, 'bold'))

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
    ual = UalComponent(8)
    ualWidget = UalWidget(root, ual)
    ualWidget.pack()
    ual.writeFirstOperand(0)
    ual.writeSecondOperand(0)
    ual.setOperation("+")
    ual.execCalc()

    root.mainloop()






