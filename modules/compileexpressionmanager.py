"""
.. module:: compileexpressionmanager
:synopsis: gestion de la compilation d'une expression. La classe CompileExpressionManager reçoit une
    expression arithmétique ou une comparaison et produit la succession d'instructions permettant
    l'exécution de cette expression.

    * CompileExpressionManager reçoit un modèle de processeur lui permettant de connaître les
        instructions disponibles et les ressources, notamment les registres et les options de l'UAL
    * CompilationManager qui délègue à CompileExpressionManager la compilation d'expression, fournit l'objet AssembleurContainer chargé de contenir le code assembleur final
"""

from typing import Union, List, Optional, Tuple

from primitives.errors import CompilationError
from primitives.variable import Variable
from primitives.litteral import Litteral
from primitives.label import Label
from primitives.operators import Operator, Operators
from primitives.register import Register, RegisterBank, RegistersStack, TempMemoryStack
from primitives.actionsfifo import ActionsFIFO

from processorengine import ProcessorEngine




class CompileExpressionManager:
    _registersBank : RegisterBank
    _registersStack: RegistersStack
    _memoryStack   : TempMemoryStack
    _actions       : ActionsFIFO

    def __init__(self, engine:ProcessorEngine, lineNumber:int):
        """        Constructeur

        :param engine: modèle de processeur utilisé
        :type engine: ProcessorEngine
        :param lineNumber: numéro de la ligne d'origine
        :type lineNumber: int
        :type lineNumber: int

        """
        self._engine = engine
        self._registersNumber = self._engine.registersNumber()
        assert self._registersNumber > 1
        self._registersBank = RegisterBank(self._registersNumber)
        self._registersStack = RegistersStack()
        self._memoryStack = TempMemoryStack()

        self._lineNumber = lineNumber
        self._actions = ActionsFIFO()


    def compile(self, fifo:ActionsFIFO) -> ActionsFIFO:
        """compile la pile de calcul

        :param fifo: file de l'expression à compiler
        :type fifo: List[Union[Operator, Variable, Litteral]]
        :param label: label du premier calcul
        :type label: Label
        :return: file des actions à affectuer en tenant compte des mouvements de registres
        :rtype: ActionsFIFO
        """
        self._actions.reset()
        while not fifo.empty:
            self._compileNext(fifo)
        return self._actions

    ### private
    def _compileNext(self, fifo:ActionsFIFO):
        """
        gère le prochaine item de la pile

        :param fifo: file de calcul en cours
        :type fifo: ActionsFIFO
        """
        item = fifo.pop()
        if isinstance(item, Variable):
            self._getNeededRegisterSpace(True)
            self._pushValue(item)
            return

        if item == Operators.SWAP.value:
            self._swapStackRegister()
            return

        if isinstance(item, Operator) and item.arity == 2:
            self._pushBinaryOperator(item)
            return

        if isinstance(item, Operator) and item.arity == 1:
            self._pushUnaryOperator(item)
            return

        # à ce stade c'est un littéral
        assert isinstance(item,Litteral)
        if fifo.empty:
            self._getNeededRegisterSpace(True)
            self._pushValue(item)
            return

        suivant = fifo.readNext()
        if isinstance(suivant, Operator) and suivant.isArithmetic and self._engine.litteralOperatorAvailable(suivant, item):
            if suivant.arity == 2:
                self._pushBinaryOperatorWithLitteral(suivant, item)
            else:
                self._pushUnaryOperatorWithLitteral(suivant, item)
            fifo.pop()
            return

        self._getNeededRegisterSpace(True)
        self._pushValue(item)

    def _freeRegister(self) -> Register:
        """Libère le dernier registre de la pile des registres.

        :return: le registre libéré
        :rtype: Register
        :raises: CompilationError s'il n'y a aucun registre à libérer

        .. warning:: ne doit pas tomber sur une mémoire temporaire
        """
        register: Optional[Register] = self._registersStack.pop()
        if register is None:
            raise CompilationError("Aucun registre à libérer.", {"lineNumber": self._lineNumber})
        assert not register.isTemp
        return register

    def _getTopStackRegister(self) -> Register:
        """
        :return: registre au sommet de la pile, sans le libérer.
        :rtype: Register
        :raises: CompilationError s'il n'y a pas d'opérande dans la pile
        .. note:: si le numéro est ``< 0``, provoque le dépilage d'un item de mémoire et retour du numéro de registre ayant accueilli le retour.
        """
        register:Optional[Register] = self._registersStack.readTop()
        if register is None:
            raise CompilationError("Pas assez d'opérande dans la pile.", {"lineNumber": self._lineNumber})
        if register.isTemp:
            self._registersStack.pop()
            newRegister = self._copyMemoryToFreeRegister(register)
            self._registersStack.push(newRegister)
            return newRegister
        return register

    def _copyMemoryToFreeRegister(self, memoryRegister:Register) -> Register:
        """Libère la mémoire temporaire et la déplace dans un registre libre

        :param memoryRegister: registre mémoire temp à libérer
        :type memoryRegister: Register
        :return: registre destination
        :rtype: Register
        :raises: CompilationError si aucun registre destination
        """
        destinationRegister = self._registersBank.getFreeRegister()
        if destinationRegister is None:
            raise CompilationError("Pas de registre disponible", {"lineNumber": self._lineNumber})
        self._actions.append(memoryRegister, destinationRegister, Operators.LOAD.value)
        return destinationRegister

    def _swapStackRegister(self):
        """Intervertit les contenus des deux derniers étages de la pile des registres

        :raises: CompilationError s'il n'y a pas assez d'opérandes pour le swap
        """
        self._registersStack.swap()

    def _getAvailableRegister(self) -> Register:
        """Retourne un registre disponible.

        :return: prochain registre disponible
        :rtype: int
        :raises: CompilationError si aucune registre n'est disponible
        """
        register = self._registersBank.getFreeRegister()
        if register is None:
            raise CompilationError("Pas de registre disponible", {"lineNumber": self._lineNumber})
        self._registersStack.push(register)
        return register

    def _UALoutputIsAvailable(self) -> bool:
        """
        :return: vrai si la sortie de l'UAL est libre
        :rtype: bool
        """
        return self._registersBank.isFree(0) or self._engine.ualOutputIsFree() and self._registersBank.hasAvailables()

    def _moveBottomRegisterToMemory(self):
        """Libère le registre en bas de la pile des registres utilisés.
        Copie le contenu dans une mémoire temporaire.
        Place -1 dans la pile des registres utilisés pour indiquer le placement en mémoire temporaire.
        :raises: CompilationError si aucun registre à déplacer
        """
        indexRegisterToCopyInTemp = self._registersStack.getLastRegisterIndex()
        if indexRegisterToCopyInTemp == -1:
            raise CompilationError("Pas de registre disponible", {"lineNumber": self._lineNumber})
        registerToCopyInTemp = self._registersStack.extract(indexRegisterToCopyInTemp)
        memoryRegister = self._copyRegisterToMemory(registerToCopyInTemp)
        self._registersStack.insert(indexRegisterToCopyInTemp, memoryRegister)

    def _copyRegisterToMemory(self, sourceRegister:Register) -> Register:
        """Ajoute au code assembleur l'opération consistant à déplacer un registre vers la mémoire.
        **Ne libère pas le registre**.

        :param sourceRegister: registre à copier
        :type sourceRegister: Register
        :return: Mémoire cible
        :rtype: Registrer
        """
        memoryRegister = self._memoryStack.getFreeRegister()
        self._actions.append(sourceRegister, memoryRegister, Operators.STORE.value)
        return memoryRegister

    def _freeZeroRegister(self):
        """Libère spécifiquement le registre 0, même s'il n'est pas au sommet de la pile.
        Aucune opération s'il est libre.
        """
        r0 = self._registersBank.getZeroRegister()
        index0 = self._registersStack.index(r0)
        if index0 < 0:
            return

        freeRegister = self._registersBank.getFreeRegister()
        if freeRegister is None:
            self._registersStack.extract(index0)
            memory = self._copyRegisterToMemory(r0)
            self._registersStack.insert(index0, memory)
            return
        self._registersStack.extract(index0)
        self._registersStack.insert(index0, freeRegister)
        self._actions.append(r0, freeRegister, Operators.MOVE.value)

    def _pushBinaryOperator(self, operator:Operator):
        """Ajoute une opération binaire.
        Libère les 2 registres au sommet de la pile, ajoute l'opération,
        Occupe le premier registre libre pour le résultat

        :param operator: opération parmi ``+``, ``-``, ``*``, ``/``, ``%``, ``&``, ``|``, ``^``
        :type operator: Operator
        """
        assert operator.arity == 2 and (operator.isArithmetic or operator.isComparaison)
        # Attention ici : ne pas libérer le premier registre tant que les 2e n'a pas été traité
        # -> il faut les libérer en même temps
        rLastCalc = self._getTopStackRegister()
        self._swapStackRegister()
        rFirstCalc = self._getTopStackRegister()
        self._swapStackRegister()
        self._freeRegister()
        self._freeRegister()

        if operator.isComparaison:
            self._actions.append(rFirstCalc, rLastCalc, operator)
            return
        registreDestination = self._getAvailableRegister()
        self._actions.append(rFirstCalc, rLastCalc, registreDestination, operator)

    def _pushBinaryOperatorWithLitteral(self, operator:Operator, litteral:Litteral):
        """Ajoute une opération binaire dont le 2e opérand est un littéral
        Libère le registre au sommet de la pile comme 1er opérande.
        Occupe le premier registre libre pour le résultat.

        :param operator: opération parmi ``+``, ``-``, ``*``, ``/``, ``%``, ``&``, ``|``, ``^``
        :type operator: Operator
        :param litteral: littéral
        :type litteral: Litteral
        """
        registreOperand = self._getTopStackRegister()
        self._freeRegister()
        registreDestination = self._getAvailableRegister()
        self._actions.append(registreOperand, litteral, registreDestination, operator)

    def _pushUnaryOperator(self, operator:Operator):
        """Ajoute une opération unaire
        Libère le registre au sommet de la pile comme opérande.
        Occupe le premier registre libre pour le résultat.

        :param operator: opération parmi ``~``, ``-``
        :type operator: Operator
        """
        registreOperand = self._getTopStackRegister()
        self._freeRegister()
        registreDestination = self._getAvailableRegister()
        self._actions.append(registreOperand, registreDestination, operator)

    def _pushUnaryOperatorWithLitteral(self, operator:Operator, litteral:Litteral):
        """Ajoute une opération unaire dont l'opérande est un littéral
        Occupe le premier registre libre pour le résultat

        :param operator: opération parmi ``~``, ``-``
        :type operator: Operator
        :param litteral: littéral
        :type litteral: Litteral
        """
        registreDestination = self._getAvailableRegister()
        self._actions.append(litteral, registreDestination, operator)

    def _pushValue(self, value:Union[Litteral,Variable]):
        """Charge une valeur dans le premier registre disponible

        :param value: valeur à charger
        :type value: Union[Litteral,Variable]
        """
        registreDestination = self._getAvailableRegister()
        if isinstance(value, Litteral):
            self._actions.append(value, registreDestination, Operators.MOVE.value)
        else:
            self._actions.append(value, registreDestination, Operators.LOAD.value)


    def _getNeededRegisterSpace(self, needUAL:bool):
        """Déplace des registres au besoin
        * Déplace le registre 0 s'il est nécessaire pour l'UAL.
        * Déplace le dernier registre vers la mémoire autant que possible ou nécessaire

        :param needUAL: le noeud nécessitera-t-il l'utilisation de l'UAL ?
        :type needUAL: bool
        """
        if not self._registersBank.hasAvailables():
            self._moveBottomRegisterToMemory()
        if needUAL and not self._UALoutputIsAvailable():
            self._freeZeroRegister()

    def getResultRegister(self) -> int:
        """
        :return: registre en haut de la pile
        :rtype: int
        """
        return self._getTopStackRegister()


if __name__=="__main__":
    from processor12bits import Processor12Bits
    from expressionparser import ExpressionParser
    listExpressions = [
        "5*(2*x+4)-x*y",
        "(((2+4)*(4+1)) - ((2+4)*(4+1))) * (((2+4)*(4+1)) - ((2+4)*(4+1)))",
        "3*x > 4"
    ]
    engine = Processor12Bits()
    cem = CompileExpressionManager(engine, -1)
    litteralSize = engine.litteralMaxSize
    for strExpression in listExpressions:
        print(strExpression)
        exp = ExpressionParser.buildExpression(strExpression)
        fifo = exp.getFIFO(litteralSize)
        print(fifo.inlineStr())
        actions = cem.compile(fifo)
        print(actions.inlineStr())
        print()

