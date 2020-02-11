"""
.. module:: executeur
   :synopsis: classe chargée de l'exécution du code binaire
"""

from typing import List

from processorengine import ProcessorEngine

class Executeur:
    __engine:ProcessorEntine
    __binary:List[int]
    __printList:List[int]
    __linePointer:int = 0
    __instructionRegister:int = 0
    __ualIsZero: bool = True
    __ualIsPos: bool = True
    __memoryAddressRegister: int = 0
    __registers:List[int]
    __currentState:int = 0
    __inputBuffer:List[int]

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

        if __currentState == 0:
            # toujours chargement de la ligne dans le registre d'adresse mémoire
            # puis incrépentation du pointeur de ligne
            # up de __currentState
            pass

            return 1

        if __currentState == 1:
            # lecture de la case mémoire pointée par le registre d'adresse mémoire
            # écriture dans le registre instruction
            # up de __currentState
            pass

            return 1

        if __currentState == 2:
            # décodade de l'instruction en utilisant :
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
            pass

        if __currentState == 3
            # Chaque état est particulier ensuite. Il faut tracer un diagramme avec tous les schémas possibles.
            # beaucoup d'instructions ne vont pas plus loin que l'état 2 ce qui limite
            # il est sans doute plus simple de prévoir des état spéciaux ensuite :
            # si toutes les instructions longues passent au niveau 3, il faudra ensuite tester pour voir dans quel cas on est
            # par contre si store ou load ont leur propre état, par exemple 4, si on est dans l'état 4 on n'a pas plus de test à faire
            # on sait déjà où on est, ce qui est plus simple.

            pass


        return __currentState

    def instructionStep(self) -> int:
        """Exécution d'une instruction complète.
        Commande donc l'exécution de plusieurs step jusqu'à ce que currentState revienne à 0, -1 ou -2

        :return: état en cours.
          -1 = halt
          -2 = attente input
          0 = début instruction,
        :rtype: int
        """
        pass

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
        pass


