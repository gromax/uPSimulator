"""
.. module:: widgets
   :synopsis: objets constitant l'interface graphique
"""
from typing import List, Dict, Any, cast

from tkinter import *
from executeurcomponents import BufferComponent, ScreenComponent, RegisterGroup, MemoryComponent, RegisterComponent, UalComponent, DataValue

class TextWidget(Frame):
    """Panneau affichant un texte avec possibilité de mettre
    une ligne en surbrillance, de numéroter les lignes
    """

    BACKGROUND:str = 'white'
    HL_BACKGROUND:str = 'orange3'
    HL_COLOR:str = 'white'
    MIN_TAB_SIZE:int = 3
    cols:int = 30
    lineNumberFormat:str = '{:03d}:   '
    lines:int = 25
    lineNumberOffset:int = 0
    _name:str = "code"
    _writeEnabled:bool = False
    _clearTabs:bool = True
    _fill:bool = False

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
                self._name = value
            elif key == "writeEnabled":
                self._writeEnabled = (value == True)
            elif key == "clearTabs":
                self._clearTabs = (value == True)
            elif key == "fill":
                self._fill = (value == True)
        if self._name != '':
            LabelFrame.__init__(self, parent, class_='TextWidget', text=self._name)
        else:
            Frame.__init__(self, parent, class_='TextWidget')

        textLines = text.split("\n")
        if self._clearTabs:
            textLines = self._execClearTabs(textLines)
        if self.lineNumberFormat != '':
            textLines = [self._addLineNumber(i, line) for i, line in enumerate(textLines)]
        if self.cols == 0:
            # on ajuste la taille de la zone de texte au contenu
            self.cols = max([len(line) for line in textLines])

        formatedText = "\n".join(textLines)
        self._textZone = Text(self, width=self.cols, height=self.lines, bg=self.BACKGROUND)
        self._textZone.insert(END, formatedText)
        if not self._writeEnabled:
            self._textZone.config(state=DISABLED)
        if self._fill:
            self._textZone.pack(fill=BOTH, expand=1)
        else:
            self._textZone.pack(padx=10, pady=10)

        self._textZone.tag_configure("HIGHLIGHTED", background=self.HL_BACKGROUND, foreground=self.HL_COLOR)

    def _addLineNumber(self, index:int, line:str) -> str:
        """Ajoute un numéro en entête de ligne

        :param index: numéro de ligne
        :type index: int
        :param line: ligne originale
        :type line: str
        :return: ligne avec entête
        :rtype: str

        :Example:
            >>> root = Tk()
            >>> tw = TextWidget(root, "")
            >>> tw._addLineNumber(47, "Ligne d'essai")
            "047:   Ligne d'essai"
        """

        return self.lineNumberFormat.format(index+self.lineNumberOffset) + line

    def _execClearTabs(self, textLines:List[str]) -> List[str]:
        """Un texte tabulé est interprété comme un texte à colonne
        chaque tabulation fait passer dans une autre colonne
        la largeur d'une colonne est égale la largeur de l'élément le plus grand
        dans cette colonne sur l'ensemble des lignes
        et au minimum à MIN_TAB_SIZE. Les tabulations sont remplacés par des espaces.

        :param textLines: texte à modifier
        :type textLines: str
        :return: texte modifié
        :rtype: str
        """

        if len(textLines) == 0:
            return textLines
        textTabLines = [ item.split("\t") for item in textLines ]
        slicesNumber = max([len(item) for item in textTabLines])
        for indexSlice in range(slicesNumber):
            size = max([len(line[indexSlice]) for line in textTabLines if len(line)>indexSlice])
            size = max(self.MIN_TAB_SIZE, size)
            for line in textTabLines:
                if len(line)>indexSlice:
                    l = len(line[indexSlice])
                    line[indexSlice] += " "*(size - l)
                else:
                    line.append(" "*size)
        formatedTextLines = [" ".join(line) for line in textTabLines]
        return formatedTextLines

    def highlightLine(self, lineIndex:int) -> None:
        """
        :param lineIndex: ligne à mettre en surbrillance
        :type lineIndex: int

        .. note:: la première ligne a l'index 0
        """
        self.clearHighlight()
        lineIndex -= self.lineNumberOffset
        if lineIndex >= 0:
            tag = str(lineIndex+1)
            self._textZone.tag_add("HIGHLIGHTED", tag+".0", tag+".end")

    def clearHighlight(self) -> None:
        """Annule toute surbrillance
        """

        self._textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')

    def clear(self) -> None:
        """Efface le contenu du texte
        """

        self._textZone.config(state=NORMAL)
        self._textZone.delete('1.0', 'end')
        if not self._writeEnabled:
            self._textZone.config(state=DISABLED)

    def insert(self, text:str) -> None:
        """Ajoute un texte à la suite

        :param text: texte à ajouter
        :type text: str
        """
        self._textZone.config(state=NORMAL)
        self._textZone.insert(END, text)
        if not self._writeEnabled:
            self._textZone.config(state=DISABLED)

    @property
    def text(self) -> str:
        """Accesseur
        :return: texte en cours d'affichage
        :rtype: str
        """
        return self._textZone.get('1.0', 'end')

class MemoryWidget(LabelFrame):
    """Panneau affichant le contenu d'une mémoire
    """
    BACKGROUND:str = 'white'
    HL_BACKGROUND:str = 'orange3'
    HL_COLOR:str = 'white'
    MODES = ("bin", "hex", "dec")
    cols:int = 30
    lineNumberFormat:str = '{:03d}:   '
    lines:int = 25
    _name:str = "mémoire"
    _mode:str = "bin"
    _isMemory:bool = False
    def __init__(self, parent, memory, **kwargs):

        for key, value in kwargs.items():
            if key == "cols" and isinstance(value, int):
                self.cols = value
            elif key == 'numbers' and isinstance(value, str):
                self.lineNumberFormat = value
            elif key == 'lines' and isinstance(value, int):
                self.lines = value
            elif key == 'name' and isinstance(value, str):
                self._name = value
            elif key == 'mode' and value in self.MODES:
                self._mode = value

        LabelFrame.__init__(self, parent, class_='MemoryWidget', text=self._name)
        self._textZone = Text(self, width=self.cols, height=self.lines, bg=self.BACKGROUND)
        self.__memory = memory
        self.__memory.bind("onwrite", self.onwrite)
        self.__memory.bind("onread", self.onread)
        self.__memory.bind("onfill", self.onfill)

        self._textZone.grid(row = 0, column = 0)
        self._textZone.tag_configure("HIGHLIGHTED", background=self.HL_BACKGROUND, foreground=self.HL_COLOR)

        if isinstance(memory, MemoryComponent):
            # il faut prévoir une adresse
            labelAddressTag = Label(self, text="Adresse")
            labelAddressTag.grid(row=1, column=0)
            self._isMemory = True
            self.__addressStringVar = StringVar()
            labelAddress = Label(self, textvariable = self.__addressStringVar)
            labelAddress.grid(row=2, column=0)
            self.__memory.bind("onwriteaddress", self.onwriteaddress)

        self.refresh()

    def selectMode(self, mode):
        """Sélection du mode d'affichage
        :param mode: mode choisi, parmi 'dec', 'bin', 'hex'
        :type mode: str
        """
        if mode in self.MODES:
            self._mode = mode
            self.refresh()

    def highlightLine(self, index:int) -> None:
        """Mise en surbrillance d'une ligne

        :param index: numéro de ligne, à partir de 0
        :type index: int
        """
        self._textZone.tag_remove("HIGHLIGHTED",  "1.0", 'end')
        lineTag = index + 1
        self._textZone.tag_add("HIGHLIGHTED", "{}.0".format(lineTag), "{}.end".format(lineTag))

    def writeValueInLine(self, value:DataValue, index:int) -> None:
        """Écrire une valeur à une certaine ligne

        :param value: valeur à écrire
        :type value: DataValue
        :param index: numéro de ligne
        :type index: int
        """
        line = (self.lineNumberFormat + value.toStr(self._mode)).format(index)
        lineTag = index + 1
        self._textZone.config(state=NORMAL)
        self._textZone.delete('{}.0'.format(lineTag), '{}.end'.format(lineTag))
        self._textZone.insert('{}.0'.format(lineTag), line)
        self._textZone.config(state=DISABLED)
        self.highlightLine(index)

    def writeAddress(self, address:DataValue) -> None:
        """Modifie l'adresse dans le registre adresse,
        met en surbrillance la ligne à l'adresse sélectionnée

        :param address: adresse choisie
        :type address: DataValue
        """

        intAddress = address.intValue
        if self._mode == "dec":
            strAddress = self.lineNumberFormat.format(intAddress) + address.toStr("udec")
        else:
            strAddress = self.lineNumberFormat.format(intAddress) + address.toStr(self._mode)
        self.__addressStringVar.set(strAddress)
        self.highlightLine(intAddress)

    def refresh(self) -> None:
        """Rafraichissement de l'affichage, après lecture du contenu
        du composant d'exécution associé
        """
        values = self.__memory.content
        lines = [(self.lineNumberFormat+item.toStr(self._mode)).format(index) for index, item in enumerate(values)]
        text = "\n".join(lines)
        self._textZone.config(state=NORMAL)
        self._textZone.delete('1.0', 'end')
        self._textZone.insert(END, text)
        self._textZone.config(state=DISABLED)
        if self._isMemory:
            self.writeAddress(self.__memory.address)

    def onfill(self, params: Any) -> None:
        """Rafraichissement de l'affichage quand le composant mémoire
        associé écrit à une adresse qui n'était pas encore utilisée

        :param params: paramètres liés à l'événement. Inutiles ici.
        :type params: Any
        """
        self.refresh()

    def onread(self, params:Dict[str, Any]) -> None:
        """Callback pour la réaction une lecture mémoire

        :param params: paramètres liés à l'événement. On utilise l'entier 'index'
        :type params: Dict[str, Any]
        """
        if "index" in params and isinstance(params["index"], int):
            index = params["index"]
            self.highlightLine(index)

    def onwrite(self, params:Dict[str, Any]) -> None:
        """Callback pour la réaction une écriture mémoire

        :param params: paramètres liés à l'événement. On utilise l'entier 'index' et le DataValue 'writed'
        :type params: Dict[str, Any]
        """
        if not ("writed" in params):
            return
        value = params["writed"]
        if not isinstance(value, DataValue):
            return
        if not ("index" in params):
            return
        index = params["index"]
        if not isinstance(index, int):
            return
        self.writeValueInLine(value, index)

    def onwriteaddress(self, params:Dict[str, Any]) -> None:
        """Callback pour la réaction à l'écriture de l'adresse

        :param params: paramètres liés à l'événement. On utilise le DataValue 'address'
        :type params: Dict[str, Any]

        .. note:: n'a aucun effet si l'executeur n'est pas de type Memory
        """
        if not self._isMemory:
            return
        if not ("address" in params):
            return
        address = params["address"]
        if not isinstance(address, DataValue):
            return
        self.writeAddress(params["address"])

class BufferWidget(LabelFrame):
    SAISIE_COLS = 18
    BUFFER_LINES = 5
    BACKGROUND = 'white'
    MAX_BUFFER_LENGTH = 30
    MODES = ("bin", "hex", "dec")
    _mode = "bin"
    __waitingInput = False

    def __init__(self, parent, bufferComp,  **options):
        if "mode" in options and options["mode"] in self.MODES:
            self._mode = options["mode"]
        LabelFrame.__init__(self, parent, class_='BufferWidget', text="Saisie")
        self.__buffer = bufferComp
        bufferComp.bind("onread", self.onreadwrite)
        bufferComp.bind("onwrite", self.onreadwrite)
        # message en entête
        self.__messageStringVar = StringVar()
        self.__messageStringVar.set("")
        label = Label(self,textvariable=self.__messageStringVar)
        label.grid(row=0, column=0, columnspan=2)
        # champ de saisie
        self.__saisie = Text(self, width=self.SAISIE_COLS, height=1, bg=self.BACKGROUND)
        self.__saisie.grid(row=1, column=0)
        self.__saisie.bind('<Return>', self.bufferize)
        # bouton de validation
        validationButton = Button(self, text=chr(8629)) # caractère ↵
        validationButton.grid(row=1, column=1)
        validationButton.bind("<Button-1>", self.bufferize)
        # contenu du buffer
        self.__bufferedText = Text(self, width=self.SAISIE_COLS+4, height=self.BUFFER_LINES, bg=self.BACKGROUND)
        self.__bufferedText.config(state=DISABLED)
        self.__bufferedText.grid(row=2, column=0, columnspan=2)
        self.refreshStrBuffer()

    def selectMode(self, mode):
        if mode in self.MODES:
            self._mode = mode
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
            self.__saisie.delete('1.0', 'end')

    def resetMessage(self):
        if self.__waitingInput:
            self.__messageStringVar.set("Saisie en attente")
        else:
            self.__messageStringVar.set("")

    def onreadwrite(self, params):
        self.__waitingInput = False
        self.__messageStringVar.set("")
        self.refreshStrBuffer()

    def onreadempty(self, params):
        self.__waitingInput = True
        self.__messageStringVar.set("Saisie en attente")

    def refreshStrBuffer(self):
        listItems = [item.toStr(self._mode) for item in self.__buffer.list]
        buffStr = "\n".join(listItems)
        self.__bufferedText.config(state=NORMAL)
        self.__bufferedText.delete('1.0', 'end')
        self.__bufferedText.insert(END, buffStr)
        self.__bufferedText.config(state=DISABLED)

class ScreenWidget(LabelFrame):
    SCREEN_COLS = 18
    SCREEN_LINES = 5
    BACKGROUND = 'white'
    MODES = ("bin", "hex", "dec")
    _mode = "bin"

    def __init__(self, parent, screen, **options):
        if "mode" in options and options["mode"] in self.MODES:
            self._mode = options["mode"]
        self.__screen = screen
        screen.bind("onclear", self.onclear)
        screen.bind("onwrite", self.onwrite)
        LabelFrame.__init__(self, parent, class_='PrintWidget', text="Écran")

        # bouton d'effacement
        button = Button(self, text='Effacer')
        button.grid(row=0, column=0)
        button.bind("<Button-1>", self.clearScreen)
        # affichage
        self._textZone = Text(self, width=self.SCREEN_COLS, height=self.SCREEN_LINES, bg=self.BACKGROUND)
        self._textZone.grid(row=1, column=0)
        self._textZone.config(state=DISABLED)
        self.refresh()

    def selectMode(self, mode):
        if mode in self.MODES:
            self._mode = mode
            self.refresh()

    def clearScreen(self, evt):
        self.__screen.clear()

    def onclear(self, params):
        self._textZone.config(state=NORMAL)
        self._textZone.delete('1.0', 'end')
        self._textZone.config(state=DISABLED)

    def onwrite(self, params):
        if "writed" in params:
            strValue = params["writed"].toStr(self._mode)
            self.addLine(strValue)

    def addLine(self, line):
        self._textZone.config(state=NORMAL)
        self._textZone.insert('end', line+"\n")
        self._textZone.config(state=DISABLED)

    def refresh(self):
        self._textZone.config(state=NORMAL)
        self._textZone.delete('1.0', 'end')
        for strItem in self.__screen.getStringList(self._mode):
            self.addLine(strItem)
        self._textZone.config(state=DISABLED)

class RegisterWidget(LabelFrame):
    BACKGROUND = 'white'
    HL_BACKGROUND = 'orange3'
    MODES = ("bin", "hex", "dec")
    __unsigned = False
    _mode = 'bin'

    def __init__(self, parent, register, **kwargs):
        for key, value in kwargs.items():
            if key == 'mode' and value in self.MODES:
                self._mode = value
            elif key == 'unsigned':
                self.__unsigned = (value == True)
        self.__register = register
        register.bind("onwrite", self.onwrite)
        register.bind("oninc", self.onwrite)
        LabelFrame.__init__(self, parent, class_='RegisterWidget', text=register.name)
        self.__valueStringVar = StringVar()
        labelValue = Label(self, textvariable = self.__valueStringVar, bg = self.BACKGROUND)
        labelValue.pack()
        self.refresh()

    def selectMode(self, mode):
        if mode in self.MODES:
            self._mode = mode
            self.refresh()

    def writeValue(self, value):
        if self.__unsigned and self._mode == 'dec':
            strValue = value.toStr('udec')
        else:
            strValue = value.toStr(self._mode)
        self.__valueStringVar.set(strValue)

    def refresh(self):
        self.writeValue(self.__register.read())

    def onwrite(self, params):
        if "writed" in params:
            self.writeValue(params["writed"])

class UalWidget(LabelFrame):
    BACKGROUND = 'white'
    MODES = ("bin", "hex", "dec")
    _mode = 'bin'

    def __init__(self, parent, ual, **kwargs):
        for key, value in kwargs.items():
            if key == 'mode' and value in self.MODES:
                self._mode = value
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
            self._mode = mode
            self.refresh()

    def refresh(self):
        self.onwriteop1({"writed":self.__ual.op1})
        self.onwriteop2({"writed":self.__ual.op2})
        self.oncalc({"result": self.__ual.read(), "iszero":self.__ual.isZero, "ispos":self.__ual.isPos})
        self.onsetoperation({"operation":self.__ual.operation})

    def onwriteop1(self, params):
        if "writed" in params:
            self.__op1StringVar.set(params["writed"].toStr(self._mode))

    def onwriteop2(self, params):
        if "writed" in params:
            self.__op2StringVar.set(params["writed"].toStr(self._mode))

    def oncalc(self, params):
        if "result" in params:
            self.__resultStringVar.set(params["result"].toStr(self._mode))
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
    COLS = 50
    LINES = 30
    MSG_LINES = 3

    def __init__(self, parent, textCode):
        self._parent = parent
        LabelFrame.__init__(self, parent, class_='InputCodeWidget', text='Votre code')
        self._programInput = TextWidget(self, textCode, cols = self.COLS, lines = self.LINES, writeEnabled = True, clearTabs = False, numbers = '', name='', fill=True)
        self._programInput.pack(padx=5, pady=5, fill=BOTH, expand=1)

    def clearProgramInput(self):
        self._programInput.clear()

    def writeProgramInput(self,text):
        self._programInput.clear()
        self._programInput.insert(text)

    @property
    def textCode(self):
        return self._programInput.text

    def highlightLine(self, lineNumber):
        self._programInput.highlightLine(lineNumber-1)


class SimulationWidget(Frame):
    def __init__(self, parent, parentWidget, executeur, textCode, asm, mode):
        Frame.__init__(self, parent, class_='SimulationWidget')
        self.asm = asm
        self._parent = parentWidget
        # grille
        for r in range(12):
            self.rowconfigure(r, weight=1)
        for c in range(5):
            self.columnconfigure(c, weight=1)

        # partie programme
        self._textCode = textCode
        self._program = TextWidget(self, textCode, cols=0, numbersdigits=2, lines=20, offset=1, name="Votre code")
        self._program.grid(row=0, column=0, rowspan=12, sticky="nsew")

        # partie asm
        self._asmFrame = TextWidget(self, str(asm), cols=0, numbertab=' ', name='Assembleur')
        self._asmFrame.grid(row=0, column=1, rowspan=12, sticky="nsew")

        self.executeur = executeur
        self._ualW = UalWidget(self, self.executeur.ual, mode=mode)
        self._inputBufferW = BufferWidget(self, self.executeur.inputBuffer, mode=mode)
        self._instrRegW = RegisterWidget(self, self.executeur.instructionRegister, unsigned = True, mode=mode)
        self._linePointerW = RegisterWidget(self, self.executeur.linePointer, unsigned = True, mode=mode)
        self._memoryW = MemoryWidget(self, self.executeur.memory, mode=mode)
        self._registersW = MemoryWidget(self, self.executeur.registers, name="Registres", lines="8", mode=mode)
        self._screenW = ScreenWidget(self, self.executeur.screen, mode=mode)

        self._inputBufferW.grid(row=0, column=2, rowspan=4, stick="nsew")
        self._screenW.grid(row=4, column=2, rowspan=4, stick="nsew")
        self._instrRegW.grid(row=8, column=2, rowspan=2, stick="nsew")
        self._linePointerW.grid(row=10, column=2, rowspan=2, stick="nsew")
        self._ualW.grid(row=0, column=3, rowspan=6, stick="nsew")
        self._registersW.grid(row=6, column=3, rowspan=6, stick="nsew")
        self._memoryW.grid(row=0, column=4, rowspan=12, stick="nsew")

        self.highlightCodeLine(0)

    @property
    def textCode(self):
        return self._textCode

    def highlightCodeLine(self, currentAsmLine:int) -> None:
        """pour un numéro de ligne en mémoire, trouve  le numéro
        de la ligne correspondante dans le programme d'origine et
        le met en surbrillance
        """
        indexCodeLine = self.asm.getLineNumber(currentAsmLine)
        self._asmFrame.highlightLine(currentAsmLine)
        self._program.highlightLine(indexCodeLine)

    def show(self):
        self.__root.mainloop()

    def stepRun(self):
        currentState = self.executeur.step()
        self.highlightCodeLine(self.executeur.currentAsmLine)
        self.addMessage(self.executeur.messages[-1])
        return currentState

    def addMessage(self, message):
        self._parent.addMessage(message)

    def selectDisplay(self, mode):
        self._ualW.selectMode(mode)
        self._inputBufferW.selectMode(mode)
        self._instrRegW.selectMode(mode)
        self._linePointerW.selectMode(mode)
        self._registersW.selectMode(mode)
        self._memoryW.selectMode(mode)
        self._screenW.selectMode(mode)

if __name__=="__main__":
    import doctest
    doctest.testmod()
