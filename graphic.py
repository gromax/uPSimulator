"""
.. module:: graphic
   :synopsis: interface graphique
"""


from tkinter import *
from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine
from executeur import Executeur
from widgets import InputCodeWidget, SimulationWidget
from errors import *





class InputCodeWindow:
    EXEMPLES = [
        ("exemple 1", "example.code"),
        ("exemple 2", "example2.code"),
        ("exemple 3", "example3.code")
    ]
    _runningSpeed = 0
    BIN_DISPLAY = 0
    DEC_DISPLAY = 1
    HEX_DISPLAY = 2
    MODES = ("bin", "dec", "hex")

    def __init__(self):
        root = Tk()
        root.title('Simulation de processeur')
        self._root = root

        menu = Menu(root)
        root['menu'] = menu

        sousMenuEdit = Menu(menu)
        menu.add_cascade(label="Edit", menu=sousMenuEdit)
        sousMenuEdit.add_command(label='Effacer', command=self.__clearProgramInput)
        sousMenuEdit.add_command(label='Modifier', command=self.__goEditMode)

        sousMenuExemples = Menu(menu)
        menu.add_cascade(label='Exemples', menu=sousMenuExemples)
        for nomExemple, nomFichier in self.EXEMPLES:
            self.__addExemple(sousMenuExemples, nomExemple, nomFichier)

        sousMenuRun = Menu(menu)
        menu.add_cascade(label="Run", menu = sousMenuRun)
        sousMenuRun.add_command(label="Compilation", command=self.__editModeCompile)
        sousMenuRun.add_separator()
        sousMenuRun.add_command(label="Step", command=self.__step)
        sousMenuRun.add_command(label="Run x1", command=self.__run_v1)
        sousMenuRun.add_command(label="Run x10", command=self.__run_v10)
        sousMenuRun.add_command(label="Run x100", command=self.__run_v100)
        sousMenuRun.add_command(label="Pause", command=self.__pause)
        sousMenuRun.add_command(label="Réinit", command=self.__reinitSim)

        sousMenuOptions = Menu(menu)
        menu.add_cascade(label="Options", menu=sousMenuOptions)
        self._currentDisplay = IntVar()
        self._currentDisplay.set(self.BIN_DISPLAY)
        sousMenuOptions.add_radiobutton(label="bin", variable=self._currentDisplay, command=self.__switchDisplay, value=self.BIN_DISPLAY)
        sousMenuOptions.add_radiobutton(label="dec", variable=self._currentDisplay, command=self.__switchDisplay, value=self.DEC_DISPLAY)
        sousMenuOptions.add_radiobutton(label="hex", variable=self._currentDisplay, command=self.__switchDisplay, value=self.HEX_DISPLAY)

        availableEngines = ProcessorEngine.AVAILABLE_ENGINES
        assert len(availableEngines) > 0
        sousMenuOptions.add_separator()
        self._currentEngineId = StringVar()
        defaultEngineName, defaultEngineId = availableEngines[0]
        self._currentEngineId.set(defaultEngineId)
        for engineName, engineId in availableEngines:
            sousMenuOptions.add_radiobutton(label=engineName, variable=self._currentEngineId, command=self.__switchEngine, value=engineId)

        self._panedWindow = PanedWindow(root, orient='vertical')
        self._panedWindow.pack(fill=BOTH, expand=1)
        self._currentWidget = InputCodeWidget(self._panedWindow, "")
        self._panedWindow.add(self._currentWidget, stick="nsew")
        #self._currentWidget.pack(fill=BOTH, expand=1)

        self._messages = Text(self._panedWindow, height=5)
        self._messages.insert(END, "Messages...\n")
        self._messages.config(state=DISABLED)
        self._panedWindow.add(self._messages, stick="nsew")

    def addMessage(self, message):
        self._messages.config(state=NORMAL)
        self._messages.insert(END, message+"\n")
        self._messages.see(END)
        self._messages.config(state=DISABLED)

    def inEditMode(self):
        return isinstance(self._currentWidget, InputCodeWidget)

    def __addExemple(self, sousMenu, nomExemple, nomFichier):
        sousMenu.add_command(label=nomExemple, command=lambda:self.__loadFile(nomFichier))

    def __loadFile(self, fileName):
        try:
            with open(fileName, 'r') as file:
                fileText = file.read()
        except Exception as e:
            self.addMessage("Impossible d'ouvrir le fichier exemple '{}'\n{}".format(fileName, e))
        else:
            if self.inEditMode():
                self._currentWidget.writeProgramInput(fileText)
            else:
                self.__doCompile(fileText)

    def __switchDisplay(self):
        d = self._currentDisplay.get()
        if 0 <= d < len(self.MODES) and not self.inEditMode():
            newMode = self.MODES[d]
            self._currentWidget.selectDisplay(newMode)

    def __switchEngine(self):
        if not self.inEditMode():
            self.__doCompile(self._currentWidget.textCode)

    def __clearProgramInput(self):
        if self.inEditMode():
            self._currentWidget.clearProgramInput()

    def __goEditMode(self):
        if not self.inEditMode():
            textCode = self._currentWidget.textCode
            self._currentWidget.destroy()
            self._currentWidget = InputCodeWidget(self._panedWindow, textCode)
            self._panedWindow.add(self._currentWidget, before=self._messages, stick="nsew", height=400)

    def __goSimMode(self, executeur, textCode, asm):
        d = self._currentDisplay.get()
        if 0 <= d < len(self.MODES):
            mode = self.MODES[d]
        else:
            mode = self.MODES[0]
        self._panedWindow.forget(self._currentWidget)
        self._currentWidget.destroy()
        self._currentWidget = SimulationWidget(self._panedWindow,self, executeur, textCode, asm, mode)
        self._panedWindow.add(self._currentWidget, before=self._messages, stick="nsew", height=400, width=1200)

    def __editModeCompile(self):
        if self.inEditMode():
            self.addMessage("Compilation...")
            textCode = self._currentWidget.textCode
            self.__doCompile(textCode)

    def __doCompile(self, textCode):
        e = self._currentEngineId.get()
        engine = ProcessorEngine(e)
        try :
            cp = CodeParser(code = textCode)
            structuredList = cp.getFinalStructuredList()
            cm = CompilationManager(engine, structuredList)
            asm = cm.asm
            executeur = Executeur(engine,asm.getDecimal())
        except (ExpressionError, CompilationError, ParseError, AttributesError) as e :
            if not e.errors is None and "lineNumber" in e.errors:
                errorMessage = "[{}] {}".format(e.errors["lineNumber"], e)
            else :
                errorMessage = str(e)
            if not self.inEditMode():
                self.__goEditMode()
            self.addMessage(errorMessage)
            if not e.errors is None and "lineNumber" in e.errors:
                self._currentWidget.highlightLine(e.errors["lineNumber"])
            else:
                print(errorMessage)
        except Exception as e:
            if not self.inEditMode():
                self.__goEditMode()
            self.addMessage(e)
        else :
            self.__goSimMode(executeur, textCode, asm)

    def __run_v1(self):
        self._runningSpeed = 1000
        self.__step()

    def __run_v10(self):
        self._runningSpeed = 100
        self.__step()

    def __run_v100(self):
        self._runningSpeed = 10
        self.__step()

    def __pause(self):
        self._runningSpeed = 0

    def __reinitSim(self):
        if not self.inEditMode():
            e = self._currentEngineId.get()
            engine = ProcessorEngine(e)
            try :
                asm = self._currentWidget.asm
                executeur = Executeur(engine, asm.getDecimal())
            except Exception as e:
                self._currentWidget.addMessage(str(e))
            else :
                textCode = self._currentWidget.textCode
                self.__goSimMode(executeur, textCode, asm)

    def __step(self):
        if self.inEditMode():
            self.__editModeCompile()
        if not self.inEditMode():
            currentState = self._currentWidget.stepRun()
            if currentState < 0:
                self._runningSpeed = 0
            if self._runningSpeed > 0:
                self._root.after(self._runningSpeed, self.__step)

    def show(self):
        self._root.mainloop()





if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





