"""
.. module:: executeur
   :synopsis: classe chargée de l'exécution du code binaire
"""

from typing import List, Tuple, Union, Sequence, Optional
from processorengine import ProcessorEngine
from executeurcomponents import BufferComponent, ScreenComponent, RegisterComponent, RegisterGroup, UalComponent, MemoryComponent, DataValue

class Executeur:
    """Identifiants des bus :
    - DATA_BUS : bus de données
    - DATA_BUS_2 : bus secondaire entre les registres et la 2e opérande UAL

    Identifiants des variables internes :
    - MEMORY: mémoire
    - MEMORY_ADDRESS: registre adresse mémoire
    - INSTRUCTION_REGISTER: registre instruction
    - LINE_POINTER: registre pointeur de ligne
    - PRINT: affichage
    - BUFFER: buffer
    - UAL: Unité Arithmétique et Logique
    - REGISTERS_OFFSET: registre 0
    """

    DATA_BUS:int = 0
    DATA_BUS_2:int = 1
    MEMORY:int = 0
    MEMORY_ADDRESS:int = 1
    INSTRUCTION_REGISTER:int = 2
    LINE_POINTER:int = 3
    PRINT:int = 4
    BUFFER:int = 5
    UAL:int = 6
    REGISTERS_OFFSET:int = 7
    __engine: ProcessorEngine
    memory: MemoryComponent
    linePointer: RegisterComponent
    instructionRegister: RegisterComponent
    registers: RegisterGroup
    inputBuffer: BufferComponent
    screen: ScreenComponent
    __instructionRegisterMask: int = 0
    __instructionRegister_regIndex:int = 0
    __currentState: int = 0
    __ualCible: int = 0
    __registerNumber: int
    currentAsmLine:int = 0
    messages:List[str]

    def __init__(self, engine:ProcessorEngine, binary:Union[List[int],List[str]]):
        """Constructeur

        :param engine: modèle de processeur
        :type engine: ProcessorEngine
        :param binary: code binaire (liste d'entiers ou représentation binaire en str)
        :type binary: List[int]
        """
        registersSize = engine.dataBits
        self.__registerNumber = engine.registersNumber()

        self.instructionRegister = RegisterComponent("Registre instruction", registersSize)
        self.linePointer = RegisterComponent("Pointeur de ligne", registersSize)
        self.registers = RegisterGroup(self.__registerNumber, registersSize)
        self.ual = UalComponent(registersSize)
        self.memory = MemoryComponent(registersSize, binary)

        self.inputBuffer = BufferComponent(registersSize)
        self.screen = ScreenComponent(registersSize)

        self.__engine = engine
        self.__mask = self.__getMask()
        self.messages = ["Initialisation"]

    @property
    def waitingInput(self) -> bool:
        """Accesseur.

        :return: processeur attend une entrée
        :rtype: bool
        """
        return self.__currentState == -2

    def __getMask(self) -> int:
        """
        :return: masque pour empêcher la saisie d'un nombre trop grand
        :rtype: int
        """
        nbits = self.__engine.dataBits
        return int("1"*nbits,2)

    def getValue(self, source:int, silent=False) -> Optional[int]:
        """lit la valeur d'un variable interne du processeur virtuel

        :param source: identifiant de la variable
        :type source: int
        :result: valeur de la variable ou False si l'identifiant est inconnu
        :rtype: Optional[int]
        """

        if source == self.MEMORY:
            return self.memory.readAddressedRegister()
        if source == self.INSTRUCTION_REGISTER:
            return self.instructionRegister.read().mask(self.__instructionRegisterMask)
        if source == self.LINE_POINTER:
            return self.linePointer.read()
        if source == self.BUFFER:
            return self.inputBuffer.read()
        if source == self.UAL:
            return self.ual.read()
        if self.REGISTERS_OFFSET <= source < self.REGISTERS_OFFSET + self.__registerNumber:
            index = source - self.REGISTERS_OFFSET
            return self.registers.read(index)
        return False

    def __setValue(self, cible:int, value:DataValue, bus:int) -> None:
        """écrit une valeur dans une variable interne du processeur virtuel

        :param cible: identifiant de la variable
        :type cible: int
        :param value: valeur à écrire
        :type value: DataValue
        """
        if bus == self.DATA_BUS:
            if cible == self.MEMORY:
                self.memory.writeAddressedRegister(value)
            elif cible == self.MEMORY_ADDRESS:
                self.memory.setAddress(value)
            elif cible == self.INSTRUCTION_REGISTER:
                self.instructionRegister.write(value)
            elif cible == self.LINE_POINTER:
                self.linePointer.write(value)
            elif cible == self.PRINT:
                self.screen.write(value)
            elif cible == self.UAL:
                self.ual.writeFirstOperand(value)
            elif self.REGISTERS_OFFSET <= cible < self.REGISTERS_OFFSET + self.__registerNumber:
                index = cible - self.REGISTERS_OFFSET
                self.registers.write(index, value)
        elif bus == self.DATA_BUS_2 and cible == self.UAL:
            self.ual.writeSecondOperand(value)

    def __transfert(self, source:int, cible:int, bus:int) -> Union[bool,DataValue]:
        """déplacement d'une donnée, depuis une source vers une cible, via un certain bus

        :param source: identifiant de source
        :type source: int
        :param cible: identifiant de la variable
        :type cible:int
        :param bus: identifiant du bus
        :type bus: int
        :result: succès
        :rtype: Union[bool,DataValue]
        """
        sourceValue = self.getValue(source)
        if isinstance(sourceValue,DataValue):
            self.__setValue(cible, sourceValue, bus)
            return sourceValue
        return False

    def __setUalInputOperands(self, registers:Sequence[int], litteral:int) -> None:
        """
        Charge les entrées de l'ual

        :param registers: adresses des registres en entrée
        :type registers: Tuple[int]
        :param litteral: éventuel littéral, défaut -1
        :type litteral: int
        """
        if len(registers) > 0:
            registerIndex = registers[0]
            self.__transfert(registerIndex+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS)
        if len(registers) > 1:
            registerIndex = registers[1]
            self.__transfert(registerIndex+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS_2)
        elif litteral != -1:
            self.__transfert(self.INSTRUCTION_REGISTER, self.UAL, self.DATA_BUS_2)

    def bufferize(self, value:int) -> None:
        """Ajoute un entier au buffer d'entrée

        :param value: valeur à bufferiser
        :type value: int
        """
        value &= self.__mask
        self.inputBuffer.write(value)

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
            sourceValue = self.__transfert(self.LINE_POINTER, self.MEMORY_ADDRESS, self.DATA_BUS)
            if isinstance(sourceValue, DataValue):
                self.currentAsmLine = sourceValue.intValue
                self.messages.append("Pointeur de ligne = {} -> Registre addresse.\nIncrémentation Pointeur de ligne".format(self.currentAsmLine))
            self.linePointer.inc()
            self.__currentState = 1

        elif self.__currentState == 1:
            # lecture de la case mémoire pointée par le registre d'adresse mémoire
            # écriture dans le registre instruction
            # up de __currentState
            sourceValue = self.__transfert(self.MEMORY, self.INSTRUCTION_REGISTER, self.DATA_BUS)
            if isinstance(sourceValue, DataValue):
                self.messages.append("Lecture mémoire -> Registre instuction : {}".format(sourceValue.toStr("bin")))
            self.__currentState = 2

        elif self.__currentState == 2:
            # décodage de l'instruction en utilisant :
            # self.__engine.instructionDecode(self.instructionRegister)
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
            instName, opRegisters, opSpecial, sizeSpecial = self.__engine.instructionDecode(self.instructionRegister.intValue)
            self.__instructionRegisterMask = 2**sizeSpecial - 1
            if instName == "halt":
                self.__currentState = -1
                self.messages.append("Halt")

            elif instName == "nop":
                self.__currentState = 0
                self.messages.append("NOP")

            elif instName == "goto":
                sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                if isinstance(sourceValue, DataValue):
                    address = sourceValue.intValue
                    self.messages.append("GOTO : ligne {} chargée dans pointeur de ligne".format(address))
                self.__currentState = 0

            elif instName == "!=":
                if(not(self.ual.isZero)):
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si ≠0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si ≠0) non effecuté.")
                    self.__currentState = 0

            elif instName == "==":
                if(self.ual.isZero):
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si =0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si =0) non effecuté.")
                    self.__currentState = 0

            elif instName == "<":
                if not (self.ual.isPos or self.ual.isZero):
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si <0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si <0) non effecuté.")
                    self.__currentState = 0

            elif instName == ">":
                if self.ual.isPos and not self.ual.isZero:
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si >0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si >0) non effecuté.")
                    self.__currentState = 0

            elif instName == ">=":
                if self.ual.isPos:
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si ≥0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si ≥0) non effecuté.")
                    self.__currentState = 0

            elif instName == "<=":
                if((self.ual.isZero)|(not(self.ual.isPos))):
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.LINE_POINTER, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        address = sourceValue.intValue
                        self.messages.append("GOTO (si ≤0): ligne {} chargée dans pointeur de ligne".format(address))
                    self.__currentState = 0
                else:
                    self.messages.append("GOTO (si ≤0) non effecuté.")
                    self.__currentState = 0

            elif instName == "input":
                sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.MEMORY_ADDRESS, self.DATA_BUS)
                if isinstance(sourceValue, DataValue):
                    address = sourceValue.intValue
                    self.messages.append("Chargement adresse : {}".format(address))
                self.__currentState = 8
                # l'état 8 est important : si on mettait -2 tout de suite, l'état -2 provoquerait un arrêt d'exécution
                # même dans des cas ou le buffer aurait été préalablement rempli

            elif instName == "print":
                register = opRegisters[0]
                self.__transfert(self.REGISTERS_OFFSET + register, self.PRINT, self.DATA_BUS)
                self.messages.append("Affichage du contenu du registre {}".format(register))
                self.__currentState = 0

            elif instName == "move":
                if len(opRegisters) == 1:
                    register = opRegisters[0]
                    sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.REGISTERS_OFFSET + register, self.DATA_BUS)
                    if isinstance(sourceValue, DataValue):
                        value = sourceValue.toStr('hex')
                        self.messages.append("Écriture de {} dans le registre {}".format(value, register))
                    self.__currentState = 0
                else:
                    registerCible, registerSource = opRegisters
                    self.__transfert(self.REGISTERS_OFFSET + registerSource, self.REGISTERS_OFFSET + registerCible, self.DATA_BUS)
                    self.messages.append("Transfert du registre {} au registre {}".format(registerSource, registerCible))
                    self.__currentState = 0

            elif instName == "store":
                self.__instructionRegister_regIndex = opRegisters[0]
                sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.MEMORY_ADDRESS, self.DATA_BUS)
                if isinstance(sourceValue, DataValue):
                    address = sourceValue.intValue
                    self.messages.append("STORE : Sélection de l'adresse {}".format(address))
                self.__currentState = 6

            elif instName == "load":
                self.__instructionRegister_regIndex = opRegisters[0]
                sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.MEMORY_ADDRESS, self.DATA_BUS)
                if isinstance(sourceValue, DataValue):
                    address = sourceValue.intValue
                    self.messages.append("LOAD : Sélection de l'adresse {}".format(address))
                self.__currentState = 7

            elif instName == "cmp":
                registerIndexGauche = opRegisters[0]
                self.__transfert(registerIndexGauche+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS)
                registerIndexDroite = opRegisters[1]
                self.__transfert(registerIndexDroite+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS_2)
                self.ual.setOperation("cmp")
                self.messages.append("CMP : Comparaison des registres {} et {}".format(registerIndexGauche, registerIndexDroite))
                self.__currentState = 3

            elif instName in ["neg", "~", "+", "-", "*", "/", "%", "&", "|", "^"]:
                self.__ualCible = opRegisters[0]

                if opSpecial != -1:
                    if len(opRegisters) == 1:
                        sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.UAL, self.DATA_BUS)
                        if isinstance(sourceValue, DataValue):
                            self.messages.append("UAL : {} -> opérande 1".format(registerIndex1, sourceValue.intValue))
                    else:
                        registerIndex = opRegisters[1]
                        self.__transfert(registerIndex+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS)
                        sourceValue = self.__transfert(self.INSTRUCTION_REGISTER, self.UAL, self.DATA_BUS_2)
                        if isinstance(sourceValue, DataValue):
                            self.messages.append("UAL : registre {} -> opérande 1 ; {} -> opérande 2".format(registerIndex, sourceValue.intValue))
                else:
                    if len(opRegisters) <= 2:
                        registerIndex = opRegisters[1]
                        self.__transfert(registerIndex+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS)
                        self.messages.append("UAL : registre {} -> opérande 1".format(registerIndex))
                    else:
                        registerIndex1 = opRegisters[1]
                        self.__transfert(registerIndex1+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS)
                        registerIndex2 = opRegisters[2]
                        self.__transfert(registerIndex2+self.REGISTERS_OFFSET, self.UAL, self.DATA_BUS_2)
                        self.messages.append("UAL : registre {} -> opérande 1 ; registre {} -> opérande 2".format(registerIndex1, registerIndex2))
                self.ual.setOperation(instName)
                self.__currentState = 4

        # Chaque état est particulier ensuite. Il faut tracer un diagramme avec tous les schémas possibles.
        # beaucoup d'instructions ne vont pas plus loin que l'état 2 ce qui limite
        # il est sans doute plus simple de prévoir des état spéciaux ensuite :
        # si toutes les instructions longues passent au niveau 3, il faudra ensuite tester pour voir dans quel cas on est
        # par contre si store ou load ont leur propre état, par exemple 4, si on est dans l'état 4 on n'a pas plus de test à faire
        # on sait déjà où on est, ce qui est plus simple.
        elif self.__currentState == 3:
            # exécution UAL CMP (sans transfert)
            self.ual.execCalc()
            self.messages.append("UAL : exécution de CMP")
            self.__currentState = 0

        elif self.__currentState == 4:
            # exécution UAL
            self.ual.execCalc()
            self.messages.append("UAL : exécution de {}".format(self.ual.operation))
            self.__currentState = 5

        elif self.__currentState == 5:
            # transfert résultat UAL
            self.__transfert(self.UAL, self.REGISTERS_OFFSET + self.__ualCible, self.DATA_BUS)
            self.messages.append("UAL : transfert résultat -> registre {}".format(self.__ualCible))
            self.__currentState = 0

        elif self.__currentState == 6:
            # store
            register = self.__instructionRegister_regIndex
            self.__transfert(self.REGISTERS_OFFSET + register, self.MEMORY, self.DATA_BUS)
            self.messages.append("STORE : transfert registre {} -> mémoire".format(register))
            self.__currentState = 0

        elif self.__currentState == 7:
            # load
            register = self.__instructionRegister_regIndex
            self.__transfert(self.MEMORY, self.REGISTERS_OFFSET + register, self.DATA_BUS)
            self.messages.append("LOAD : transfert mémoire -> registre {}".format(register))
            self.__currentState = 0

        elif self.__currentState == 8 or self.__currentState == -2:
            # On charge le contenu du buffer si celui-ci n'est pas vide
            # On attend sinon
            if self.__transfert(self.BUFFER, self.MEMORY, self.DATA_BUS):
                self.messages.append("INPUT : transfert buffer -> mémoire")
                self.__currentState = 0
            else:
                self.messages.append("INPUT : attente saisie utilisateur")
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
        return f'ligne = {self.linePointer.read()}'

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
    print(myExec.screen.getStringList("bin"))

    tests = [ 'example.code' ]
    '''
    tests = [
        'example.code',
        'example2.code'
    ]
    '''

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
        binary16 = cm16.asm.getDecimal()
        myExec16 = Executeur(engine16,binary16)
        myExec16.bufferize(88)
        myExec16.nonStopRun()
        print("PrintList")
        print(myExec16.screen.getStringList("bin"))
        print()

        cm12 = CompilationManager(engine12, structuredList)
        print("Execution 12 bits")
        binary12=cm12.asm.getDecimal()
        myExec12 = Executeur(engine12,binary12)
        myExec12.bufferize(88)
        myExec12.nonStopRun()
        print("PrintList")
        print(myExec12.screen.getStringList("bin"))
        print()

