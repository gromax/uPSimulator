"""
.. module:: executeur
   :synopsis: classe chargée de l'exécution du code binaire
"""

from typing import List, Tuple, Union, Sequence
from processorengine import ProcessorEngine

class Executeur:
    __engine: ProcessorEngine
    __memory: List[int]
    __printList: List[int]
    __linePointer: int = 0
    __instructionRegister: int = 0
    __ualIsZero: bool = True
    __ualIsPos: bool = True
    __ualInput: Tuple[str, Tuple[int], int]
    __memoryAddressRegister: int = 0
    __registers: List[int]
    __currentState: int = 0
    __inputBuffer: List[int]
    __ualOp1: int = 0
    __ualOp2: int = 0
    __ualCible: int = 0
    __ualCommand: str = ""

    def __init__(self, engine:ProcessorEngine, binary:Union[List[int],List[str]]):
        """Constructeur

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :param binary: code binaire (liste d'entiers ou représentation binaire en str)
        :type binary: List[int]
        """
        self.__engine = engine
        self.__mask = self.__getMask()
        self.__memory = []
        for item in binary:
            if isinstance(item,str):
                self.__memory.append(int(item,2) & self.__mask)
            else:
                self.__memory.append(item & self.__mask)
        self.__printList = []
        self.__registers = [0]*engine.registersNumber()
        self.__inputBuffer = []

    @property
    def printList(self) -> List[int]:
        """Accesseur.

        :return: liste des valeurs à afficher
        :rtype: List[int]
        """
        return self.__printList

    @property
    def waitingInput(self) -> bool:
        """Accesseur.

        :return: processeur attend une entrée
        :rtype: bool
        """
        return self.__currentState == -2

    def __getMask(self) -> int:
        """
        :return:masque pour empêcher la saisie d'un nombre trop grand
        :rtype:int
        """
        nbits = self.__engine.getDataBits()
        return int("1"*nbits,2)

    '''
    Fonctions correspondant à une mise à une modification d'un organe du processeur
    '''
    def __readMemory(self) -> int:
        """
        :return: valeur mémoire contenue à l'adresse stockée dans __memoryAddressRegister, 0 par défaut
        :rtype:int
        """
        address = self.__memoryAddressRegister
        if address < len(self.__memory):
            return self.__memory[address]
        return 0

    def __writeMemory(self, value:int) -> None:
        """
        :param value: valeur à écrire dans la mémoire
        :type value:int
        """
        address = self.__memoryAddressRegister
        self.__memory[address] = value

    def __setMemoryAddressRegister(self, address:int) -> None:
        """Modifie le registre d'adresse

        :param address: nouvelle adresse
        :type address: int
        """
        self.__memoryAddressRegister = address

    def __setUalInputOperands(self, registers:Sequence[int], litteral:int) -> None:
        """
        Charge les entrées de l'ual

        :param registers: adresses des registres en entrée
        :type registers: Tuple[int]
        :param litteral: éventuel littéral, défaut -1
        :type litteral: int
        """
        ops = []
        if len(registers) > 0:
            registerIndex = registers[0]
            ops.append(self.__registers[registerIndex])
        if len(registers) > 1:
            registerIndex = registers[1]
            ops.append(self.__registers[registerIndex])
        elif litteral != -1:
            ops.append(litteral)
        if len(ops) == 1:
            self.__ualOp1 = ops[0]
        elif len(ops) == 2:
            self.__ualOp1, self.__ualOp2 = ops

    def bufferize(self, value:int) -> None:
        """Ajoute un entier au buffer d'entrée

        :param value: valeur à bufferiser
        :type value: int
        """
        value &= self.__mask
        self.__inputBuffer.append(value)

    def __executeUAL(self):
        """Exécute le calcul
        """
        op1 = self.__ualOp1
        op2 = self.__ualOp2
        if self.__ualCommand == "cmp":
            self.__ualIsZero = ( (op1 - op2) == 0 )
            self.__ualIsPos = ( (op1 - op2) > 0 )
        else:
            outputRegister = self.__ualCible
            if self.__ualCommand == "neg" or self.__ualCommand == "~":
                op1 = self.__ualOp1
                if self.__ualCommand == "neg":
                    result = (-op1) & self.__mask
                else:
                    result = (~op1) and self.__mask
                self.__registers[outputRegister] = result
            else:
                if self.__ualCommand == "+":
                    result = (op1 + op2) & self.__mask
                elif self.__ualCommand == "-":
                    result = (op1 - op2) & self.__mask
                elif self.__ualCommand == "*":
                    result = (op1 * op2) & self.__mask
                elif self.__ualCommand == "/":
                    result = op1 // op2
                elif self.__ualCommand == "%":
                    result = op1 % op2
                elif self.__ualCommand == "&":
                    result = op1 & op2
                elif self.__ualCommand == "|":
                    result = op1 | op2
                elif self.__ualCommand == "^":
                    result = op1 ^ op2
                self.__registers[outputRegister] = result

    def step(self) -> int:
        """Exécution d'un pas.
        Il s'agit d'un pas élémentaire, il en faut plusieurs pour exécuter l'ensemble de l'instruction.
        Le nombre de pas nécessaire dépend du type d'instruction.

        :return: état en cours.
          -1 = halt
          -2 = attente input
          0 = début instruction,
          1 <= état interne du processeur correspondant au déroulement de l'instruction
        :rtype: int
        """
        if self.__currentState == 0:
            # toujours chargement de la ligne dans le registre d'adresse mémoire
            # puis incrémentation du pointeur de ligne
            # up de __currentState
            self.__setMemoryAddressRegister(self.__linePointer)
            self.__linePointer += 1
            self.__currentState = 1

        elif self.__currentState == 1:
            # lecture de la case mémoire pointée par le registre d'adresse mémoire
            # écriture dans le registre instruction
            # up de __currentState
            self.__instructionRegister = self.__readMemory()
            self.__currentState = 2

        elif self.__currentState == 2:
            # décodage de l'instruction en utilisant :
            # self.__engine.instructionDecode(self.__instructionRegister)
            # voir la doc de la fonction
            # il faut stocker la réponse dans des attributs ad hoc pour pouvoir les utiliser au pas suivants (le cas échéant)
            # la suite va dépendre de l'instruction, les currentState pour certains cas sont à choisir (? dans la suite) :
            #     halt : -1 -> currentState
            #     store ou load chargent l'adresse cible dans le registre d'adresse mémoire, ? -> currentState
            #     calculs placent les entrées de l'UAL et demandent calcul, ? -> currentState
            #     move fait transfert direct et termine, 0 -> currentState
            #     saut charge (ou pas selon si conditionnel) l'adresse cible dans pointeur de ligne, 0 -> currentState
            #     print charge le registre dans la pile Print puis 0 -> currentState
            #     input charge adresse cible dans registre adresse, ? -> currentState
            #     dans l'état suivant pour input, il faudra lire dans le buffer. Si buffer vide, nécessitera de passer à l'état -2
            instName, opRegisters, opSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            if instName == "halt":
                self.__currentState = -1

            elif instName == "goto":
                self.__linePointer = opSpecial
                self.__currentState = 0

            elif instName == "!=":
                if(not(self.__ualIsZero)):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == "==":
                if(self.__ualIsZero):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == "<":
                if(not(self.__ualIsPos))&(not(self.__ualIsZero)):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == ">":
                if(self.__ualIsPos):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == ">=":
                if((self.__ualIsZero)|(self.__ualIsPos)):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == "<=":
                if((self.__ualIsZero)|(not(self.__ualIsPos))):
                    self.__linePointer = opSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            elif instName == "input":
                self.__setMemoryAddressRegister(opSpecial)
                self.__currentState = 6
                # l'état 6 est important : si on mettait -2 tout de suite, l'état -2 provoquerait un arrêt d'exécution
                # même dans des cas ou le buffer aurait été préalablement rempli

            elif instName == "print":
                op = opRegisters[0]
                self.__printList.append(self.__registers[op])
                self.__currentState = 0

            elif instName == "move":
                if len(opRegisters) == 1:
                    op = opRegisters[0]
                    self.__registers[op] = opSpecial
                    self.__currentState = 0
                else:
                    opCible, opSource = opRegisters
                    self.__registers[opCible] = self.__registers[opSource]
                    self.__currentState = 0

            elif instName == "store":
                self.__setMemoryAddressRegister(opSpecial)
                self.__currentState = 4

            elif instName == "load":
                self.__setMemoryAddressRegister(opSpecial)
                self.__currentState = 5

            elif instName == "cmp":
                self.__setUalInputOperands(opRegisters, opSpecial)
                self.__ualCommand = instName
                self.__currentState = 3

            elif instName in ["neg", "~", "+", "-", "*", "/", "%", "&", "|", "^"]:
                self.__ualCible = opRegisters[0]
                self.__setUalInputOperands(opRegisters[1:], opSpecial)
                self.__ualCommand = instName
                self.__currentState = 3

        elif self.__currentState == 3:
            # Chaque état est particulier ensuite. Il faut tracer un diagramme avec tous les schémas possibles.
            # beaucoup d'instructions ne vont pas plus loin que l'état 2 ce qui limite
            # il est sans doute plus simple de prévoir des état spéciaux ensuite :
            # si toutes les instructions longues passent au niveau 3, il faudra ensuite tester pour voir dans quel cas on est
            # par contre si store ou load ont leur propre état, par exemple 4, si on est dans l'état 4 on n'a pas plus de test à faire
            # on sait déjà où on est, ce qui est plus simple.
            self.__executeUAL()
            self.__currentState = 0

        elif self.__currentState == 4:
            # store
            instName, opRegisters, opSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            r = opRegisters[0]
            valueToStore = self.__registers[r]
            self.__writeMemory(valueToStore)
            self.__currentState = 0

        elif self.__currentState == 5:
            # load
            instName, opRegisters, opSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            self.__registers[opRegisters[0]] = self.__readMemory()
            self.__currentState = 0

        elif self.__currentState == 6 or self.__currentState == -2:
            # On charge le contenu du buffer si celui-ci n'est pas vide
            # On attend sinon
            if self.__inputBuffer!=[]:
                valueToStore = self.__inputBuffer.pop(0)
                self.__memory[self.__memoryAddressRegister] = valueToStore
                self.__currentState = 0
            else:
                self.__currentState = -2


        return self.__currentState


    def instructionStep(self) -> int:
        """Exécution d'une instruction complète.
        Commande donc l'exécution de plusieurs step jusqu'à ce que currentState revienne à 0, -1 ou -2

        :return: état en cours.
          -1 = halt
          -2 = attente input
          0 = début instruction,
        :rtype: int
        """
        while (self.step() > 0 ):
            pass
        return self.__currentState

    def nonStopRun(self) -> int:
        """Exécution du programme en continu
        Commande donc l'exécution de plusieurs step jusqu'à ce que currentState revienne -1 ou -2

        :return: état en cours.
          -1 = halt
          -2 = attente input
        :rtype: int

        ..warning::
          Si le programme boucle, l'instruction bouclera aussi.
          De plus, ce programme prend la main pour toute une exécution.
          Ne convient donc pas au cas d'une visualisation avec interface graphique devant se remettre à jour en parallèle de l'exécution.
        """
        while (self.step() >= 0 ):
            pass
        return self.__currentState

    def __str__(self) -> str :
        return f'ligne = {self.__linePointer}\n'


if __name__ == '__main__':
    from processorengine import ProcessorEngine
    from codeparser import CodeParser
    from compilemanager import CompilationManager
    engine = ProcessorEngine()

    print("TEST 0")
    binary = [  '0100100000000000',
                '0111000000011010',
                '0100100000000000',
                '0111000000011011',
                '0011000000011010',
                '0100100100001010',
                '0001100000100000',
                '0001010000001101',
                '0011000000011011',
                '0100100101100100',
                '0001100000100000',
                '0001010000001101',
                '0000100000010111',
                '0011000000011010',
                '1010000000000011',
                '0101000000000000',
                '1000000000000001',
                '0111000000011010',
                '0011000000011011',
                '0011001000011010',
                '0110000000000001',
                '0111000000011011',
                '0000100000000100',
                '0011000000011011',
                '0010000000000000',
                '0000000000000000',
                '0000000000000000',
                '0000000000000000']

    myExec = Executeur(engine, binary)

    myExec.nonStopRun()
    print(myExec.printList)

    tests = [
        'example.code',
        'example2.code'
    ]

    engine16 = ProcessorEngine()
    engine12 = ProcessorEngine("12bits")

    for testFile in tests:
        print("#### Fichier "+testFile)
        cp = CodeParser(filename = testFile)
        structuredList = cp.getFinalStructuredList()

        print("Programme structuré :")
        print()
        for item in structuredList:
            print(item)
        print()

        cm16 = CompilationManager(engine16, structuredList)

        print("Execution 16 bits")
        binary16 = cm16.getAsm().getDecimal()
        myExec16 = Executeur(engine16,binary16)
        myExec16.bufferize(88)
        myExec16.nonStopRun()
        print("PrintList")
        print(myExec16.printList)
        print()

        cm12 = CompilationManager(engine12, structuredList)
        print("Execution 12 bits")
        binary12=cm12.getAsm().getDecimal()
        myExec12 = Executeur(engine12,binary12)
        myExec12.bufferize(88)
        myExec12.nonStopRun()
        print("PrintList")
        print(myExec12.printList)
        print()
