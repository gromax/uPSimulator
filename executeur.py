"""
.. module:: executeur
   :synopsis: classe chargée de l'exécution du code binaire
"""

from typing import List, Tuple
from processorengine import ProcessorEngine

class Executeur:
    __engine:ProcessorEngine
    __binary:List[int]
    __printList:List[int]
    __linePointer:int = 0
    __instructionRegister:int = 0
    __ualIsZero: bool = True
    __ualIsPos: bool = True
    __ualInput: Tuple[str, Tuple[int], int]
    __memoryAddressRegister: int = 0
    __registers: List[int]
    __currentState: int = 0
    __inputBuffer: List[int]

    def __init__(self, engine:ProcessorEngine, binary:List[int]):
        """Constructeur

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :param binary: code binaire
        :type binary: List[int]
        """
        self.__engine = engine
        self.__binary = binary
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

    def bufferize(self, value:int) -> None:
        """Ajoute un entier au buffer d'entrée

        :param value: valeur à bufferiser
        :type value: int
        """
        self.__inputBuffer.append(value)

    def UAL(self, ualInput: Tuple[str, Tuple[int]] ):
        instructionName = ualInput[0]
        instructionRegisterList = ualInput[1]
        litteralOp = ualInput[2]

        if instructionName == "cmp":
            op1 = self.__registers[instructionRegisterList[0]]
            op2 = self.__registers[instructionRegisterList[1]]
            self.__ualIsZero = ( (op1 - op2) == 0 )
            self.__ualIsPos = ( (op1 - op2) > 0 )
        else:
            outputRegister = instructionRegisterList[0]
            if instructionName == "neg":
                if litteralOp == -1:
                    op1 = self.__registers[instructionRegisterList[1]]
                else:
                    op1 = litteralOp
                self.__registers[outputRegister] = -op1
            elif instructionName == "~":
                op1 = self.__registers[instructionRegisterList[1]]
                if op1 != 0:
                    self.__registers[outputRegister] = 0
                else:
                    self.__registers[outputRegister] = 1
            else:
                op1 = self.__registers[instructionRegisterList[1]]
                if litteralOp == -1:
                    op2 = self.__registers[instructionRegisterList[2]]
                else:
                    op2 = litteralOp
                
                if instructionName == "+":
                    self.__registers[outputRegister] = op1 + op2
                elif instructionName == "-":
                    self.__registers[outputRegister] = op1 - op2
                elif instructionName == "*":
                    self.__registers[outputRegister] = op1 * op2                
                elif instructionName == "/":
                    self.__registers[outputRegister] = op1 // op2
                elif instructionName == "%":
                    self.__registers[outputRegister] = op1 % op2
                elif instructionName == "&":
                    self.__registers[outputRegister] = (op1!=0)&(op2!=0)
                elif instructionName == "|":
                    self.__registers[outputRegister] = (op1!=0)|(op2!=0)               
                elif instructionName == "^":
                    self.__registers[outputRegister] = (op1!=0)^(op2!=0)


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
            self.__memoryAddressRegister = self.__linePointer
            self.__linePointer += 1
            self.__currentState += 1

        elif self.__currentState == 1:
            # lecture de la case mémoire pointée par le registre d'adresse mémoire
            # écriture dans le registre instruction
            # up de __currentState
            self.__instructionRegister = self.__binary[self.__memoryAddressRegister]
            self.__currentState += 1

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
            instName, instRegList, intSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            if (instName == "halt"):
                self.__currentState = -1

            if (instName == "goto"):
                self.__linePointer = intSpecial
                self.__currentState = 0

            if (instName == "!="): 
                if(not(self.__ualIsZero)):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            if (instName == "=="): 
                if(self.__ualIsZero):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            if (instName == "<"): 
                if(not(self.__ualIsPos))&(not(self.__ualIsZero)):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            if (instName == ">"): 
                if(self.__ualIsPos):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0

            if (instName == ">="): 
                if((self.__ualIsZero)|(self.__ualIsPos)):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0
                
            if (instName == "<="): 
                if((self.__ualIsZero)|(not(self.__ualIsPos))):
                    self.__linePointer = intSpecial
                    self.__currentState = 0
                else:
                    self.__currentState = 0
                
            if (instName == "input"):
                self.__memoryAddressRegister = intSpecial
                self.__currentState = -2

            if (instName == "print"):
                self.__printList.append(self.__registers[instRegList[0]])
                self.__currentState = 0

            if (instName == "move"):
                if len(instRegList) == 1:
                    self.__registers[instRegList[0]] = intSpecial
                    self.__currentState = 0
                else:
                    self.__registers[instRegList[0]] = self.__registers[instRegList[1]]
                    self.__currentState = 0 

            if (instName == "store"):
                self.__memoryAddressRegister = intSpecial
                self.__currentState = 4

            if (instName == "load"):
                self.__memoryAddressRegister = intSpecial
                self.__currentState = 5

            if (instName in ["cmp", "neg", "~", "+", "-", "*", "/", "%", "&", "|", "^"]):
                self.__ualInput = (instName, instRegList, intSpecial)
                self.__currentState += 1



        elif self.__currentState == 3:
            # Chaque état est particulier ensuite. Il faut tracer un diagramme avec tous les schémas possibles.
            # beaucoup d'instructions ne vont pas plus loin que l'état 2 ce qui limite
            # il est sans doute plus simple de prévoir des état spéciaux ensuite :
            # si toutes les instructions longues passent au niveau 3, il faudra ensuite tester pour voir dans quel cas on est
            # par contre si store ou load ont leur propre état, par exemple 4, si on est dans l'état 4 on n'a pas plus de test à faire
            # on sait déjà où on est, ce qui est plus simple.
            self.UAL(self.__ualInput)
            self.__currentState = 0

        elif self.__currentState == -2:
            # On charge le contenu du buffer si celui-ci n'est pas vide
            # On attend sinon
            if self.__inputBuffer!=[]:
                bintoStore = format(self.__inputBuffer.pop(), '0'+str(self.__engine.getDataBits())+'b')
                self.__binary[self.__memoryAddressRegister] = bintoStore
                self.__currentState = 0
            else:
                self.waitingInput

        elif self.__currentState == 4:
            # store
            instName, instRegList, intSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            bintoStore = format(self.__registers[instRegList[0]], '0'+str(self.__engine.getDataBits())+'b')
            self.__binary[self.__memoryAddressRegister] = bintoStore
            self.__currentState = 0

        elif self.__currentState == 5:
            # load
            instName, instRegList, intSpecial = self.__engine.instructionDecode(self.__instructionRegister)
            self.__registers[instRegList[0]] = int(self.__binary[self.__memoryAddressRegister],2)
            self.__currentState = 0

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
        self.step()
        while (self.__currentState > 0 ):
            self.step()

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
        while (self.__currentState != -1 ):
            self.step()

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

    myExec = Executeur(engine,binary)

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
        print("Assembleur avec la structure 16 bits :")
        print()
        print(cm16.getAsm())
        print()
        print("Binaire avec la structure 16 bits :")
        print()
        print(cm16.getAsm().getBinary())
        print()

        print("Execution 16 bits")
        binary16=cm16.getAsm().getBinary()
        binary16 = binary16.split("\n")
        myExec16 = Executeur(engine16,binary16)
        myExec16.bufferize(88)
        myExec16.nonStopRun()
        print("PrintList")
        print(myExec16.printList)
        print()

        cm12 = CompilationManager(engine12, structuredList)
        print("Assembleur avec la structure 12 bits :")
        print()
        print(cm12.getAsm())
        print()
        print("Binaire avec la structure 12 bits :")
        print()
        print(cm12.getAsm().getBinary())
        print()

        print("Execution 12 bits")
        binary12=cm12.getAsm().getBinary()
        binary12 = binary12.split("\n")
        myExec12 = Executeur(engine12,binary12)
        myExec12.bufferize(88)  
        myExec12.nonStopRun()
        print("PrintList")
        print(myExec12.printList)
        print()

