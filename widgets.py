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
    __waitingInput = True

    def __init__(self, parent, bufferComp):
        LabelFrame.__init__(self, parent, class_='BufferWidget', text="Saisie")
        self.__buffer = bufferComp
        bufferComp.bind("onread", self.onreadwrite)
        bufferComp.bind("onwrite", self.onreadwrite)
        # message en entête
        self.__messageStringVar = StringVar()
        self.__messageStringVar.set("Saisie")
        label = Label(self,textvariable=self.__messageStringVar)
        label.grid(row=0, column=0, columnspan=2)
        # champ de saisie
        self.__saisie = Text(self, width=self.SAISIE_COLS, height=1, bg=self.BACKGROUND)
        self.__saisie.grid(row=1, column=0)
        # bouton de validation
        validationButton = Button(self, text='Entrer')
        validationButton.grid(row=1, column=1)
        validationButton.bind("<Button-1>", self.bufferize)
        # contenu du buffer
        self.__bufferedStringVar = StringVar()
        bufferedLabel = Label(self, textvariable=self.__bufferedStringVar, relief='groove')
        bufferedLabel.grid(row=2, column=0, columnspan=2)
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
            self.__messageStringVar.set('Nombre entier attendu !')
            self.after(1000, self.resetMessage)
        else:
            self.__buffer.write(value)

    def resetMessage(self):
        if self.__waitingInput:
            self.__messageStringVar.set("Saisie en attente")
        else:
            self.__messageStringVar.set('Saisie')

    def onreadwrite(self, params):
        self.__waitingInput = False
        self.__messageStringVar.set("Saisie")
        self.refreshStrBuffer()

    def onreadempty(self, params):
        self.__waitingInput = True
        self.__messageStringVar.set("Saisie en attente")

    def refreshStrBuffer(self):
        buffStr = " ; ".join([item.toStr(self.__mode) for item in self.__buffer.list])
        print(buffStr)
        if len(buffStr) == 0:
            buffStr = "Buffer vide"
        elif len(buffStr) > self.MAX_BUFFER_LENGTH:
            buffStr = buffStr[:self.MAX_BUFFER_LENGTH]+"..."
        self.__bufferedStringVar.set(buffStr)

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

class InputCodeWidget(LabelFrame):
    # Cadre pour la saisie du code avec champ message erreurs
    def __init__(self, parent, compileCallBack):
        LabelFrame.__init__(self, parent, class_='InputCodeWidget', text='Votre code')
        self.__programInput = Text(self, width = 30, height = 10, bg = 'white')
        self.__programInput.pack(padx=10, pady=10)
        self.__programInput.bind('<Double-Button-1>', self.__clear_programInput)

        compileButton = Button(self, text='Compile', command = self.__doCompile)
        compileButton.pack()

        self.__errorStringVar = StringVar()
        self.__errorStringVar.set("Aucun message...")
        errorMessageFrame = Message(self, width = 300, textvariable=self.__errorStringVar, bg = '#faa', relief='groove')
        errorMessageFrame.pack(padx=10, pady=10)
        self.__compileCallBack = compileCallBack

    def __clear_programInput(self,event):
        self.__programInput.delete('1.0', 'end')

    def __doCompile(self):
        self.__errorStringVar.set("Compilation...")
        textCode = self.__programInput.get('1.0', 'end')
        self.__compileCallBack(textCode, self)

    def writeMessage(self, message):
        self.__errorStringVar.set(message)



class SimulationWidget(Frame):
    def __init__(self, parent, executeur, textCode, asm):
        Frame.__init__(self, parent, class_='SimulationWidget')
        self.asm = asm
        # grille
        '''
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        '''

        # partie programme
        self.__program = TextWidget(self, textCode, numbersdigits=2, lines=20, offset=1, name="Votre code")
        self.__program.grid(row=1, column=0, columnspan=3, rowspan=9)

        stepButton = Button(self, width=10, height=1, text='Pas')
        stepButton.grid(row=0, column=0)
        stepButton.bind('<Button-1>', self.stepRun)
        reinitButton = Button(self, width=10, height=1, text='Réinit')
        reinitButton.grid(row=0, column=1)
        goButton = Button(self, width=10, height=1, text='Réinit')
        goButton.grid(row=0, column=2)

        self.__messages = Text(self, width=self.__program.cols, height=2)
        self.__messages.grid(row=10, column=0, rowspan=2, columnspan=3)

        # partie asm
        self.__asmFrame = TextWidget(self, str(asm), cols=0, numbertab=' ', name='Assembleur')
        self.__asmFrame.grid(row=0, column=3, rowspan=12)

        self.executeur = executeur
        ualW = UalWidget(self, self.executeur.ual)
        inputBufferW = BufferWidget(self, self.executeur.inputBuffer)
        instrRegW = RegisterWidget(self, self.executeur.instructionRegister, unsigned = True)
        linePointerW = RegisterWidget(self, self.executeur.linePointer, unsigned = True)
        memoryW = MemoryWidget(self, self.executeur.memory)
        registersW = MemoryWidget(self, self.executeur.registers, name="Registres", lines="8")
        screenW = ScreenWidget(self, self.executeur.screen)

        inputBufferW.grid(row=0, column=4, rowspan=4)
        screenW.grid(row=4, column=4, rowspan=4)
        instrRegW.grid(row=8, column=4, rowspan=2)
        linePointerW.grid(row=10, column=4, rowspan=2)
        ualW.grid(row=0, column=5, rowspan=6)
        registersW.grid(row=6, column=5, rowspan=6)
        memoryW.grid(row=0, column=6, rowspan=12)

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
    root = Tk()
    saisie = BufferWidget(root, BufferComponent(8))
    saisie.pack()



    root.mainloop()






