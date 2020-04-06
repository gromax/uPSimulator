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
    def __init__(self):
        root = Tk()
        root.title('Simulation de processeur')
        self._root = root

        menu = Menu(root)
        root['menu'] = menu
        menu.add_command(label='Compilation', command=self.__editModeCompile)
        menu.add_command(label='Effacer', command=self.__clearProgramInput)

        sousMenuExemples = Menu(menu)
        menu.add_cascade(label='Exemples', menu=sousMenuExemples)
        for nomExemple, nomFichier in self.EXEMPLES:
            self.__addExemple(sousMenuExemples, nomExemple, nomFichier)

        sousMenuRun = Menu(menu)
        menu.add_cascade(label="Run", menu = sousMenuRun)
        sousMenuRun.add_command(label="step", command=self.__step)
        sousMenuRun.add_command(label="Run x1", command=self.__run_v1)
        sousMenuRun.add_command(label="Run x10", command=self.__run_v10)
        sousMenuRun.add_command(label="Run x100", command=self.__run_v100)
        sousMenuRun.add_command(label="Pause", command=self.__pause)
        sousMenuRun.add_command(label="Réinit", command=self.__reinitSim)


        self._currentWidget = InputCodeWidget(root)
        self._currentWidget.pack()

    def inEditMode(self):
        return isinstance(self._currentWidget, InputCodeWidget)

    def __addExemple(self, sousMenu, nomExemple, nomFichier):
        sousMenu.add_command(label=nomExemple, command=lambda:self.__loadFile(nomFichier))

    def __loadFile(self, fileName):
        try:
            with open(fileName, 'r') as file:
                fileText = file.read()
        except Exception as e:
            self.writeMessage("Impossible d'ouvrir le fichier exemple '{}'\n{}".format(fileName, e))
        else:
            if self.inEditMode():
                self._currentWidget.writeProgramInput(fileText)
            else:
                self.__doCompile(fileText)

    def __clearProgramInput(self):
        if self.inEditMode():
            self._currentWidget.clearProgramInput()

    def __goEditMode(self):
        pass

    def __goSimMode(self, executeur, textCode, asm):
        self._currentWidget.destroy()
        self._currentWidget = SimulationWidget(self._root, executeur, textCode, asm)
        self._currentWidget.pack()

    def __editModeCompile(self):
        if self.inEditMode():
            self._currentWidget.writeMessage("Compilation...")
            textCode = self._currentWidget.getCode()
            self.__doCompile(textCode)

    def __doCompile(self, textCode):
        engine = ProcessorEngine()
        try :
            cp = CodeParser(code = textCode)
            structuredList = cp.getFinalStructuredList()
            cm = CompilationManager(engine, structuredList)
            asm = cm.getAsm()
            asm.removeEmptyLines()
            executeur = Executeur(engine,asm.getDecimal())
        except (ExpressionError, CompilationError, ParseError, AttributesError) as e :
            if "lineNumber" in e.errors:
                errorMessage = "[{}] {}".format(e.errors["lineNumber"], e)
            else :
                errorMessage = str(e)
            if self.inEditMode():
                self._currentWidget.writeMessage(errorMessage)
                if "lineNumber" in e.errors:
                    self._currentWidget.highlightLine(e.errors["lineNumber"])
            else:
                print(errorMessage)
        except Exception as e:
            if self.inEditMode() != None:
                self._currentWidget.writeMessage(e)
            else:
                print(e)
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
            engine = ProcessorEngine()
            try :
                asm = self._currentWidget.asm
                executeur = Executeur(engine,asm.getDecimal())
            except Exception as e:
                self._currentWidget.addMessage(str(e))
            else :
                textCode = self._currentWidget.textCode
                self.__goSimMode(executeur, textCode, asm)

    def __step(self):
        if self.inEditMode():
            self.__editModeCompile()
        if not self.inEditMode():
            self._currentWidget.stepRun()
            if self._runningSpeed > 0:
                self._root.after(self._runningSpeed, self.__step)

    def show(self):
        self._root.mainloop()





if __name__=="__main__":
    g = InputCodeWindow()
    g.show()





