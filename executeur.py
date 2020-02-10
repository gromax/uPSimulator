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
    __waitingInput: bool = False
    __registers:List[int]
    __currentState:int = 0

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

        :return: processeur attend une entrée, à fournir via la commande step(value)
        :rtype: bool
        """
        return self.__waitingInput

    def step(self, value:int = 0) -> int:
        """Exécution d'un pas.
        Il s'agit d'un pas élémentaire, il en faut plusieurs pour exécuter l'ensemble de l'instruction.
        Le nombre de pas nécessaire dépend du type d'instruction.

        :param value: valeur fournie, utile en cas d'attente d'input (sinon ignorée)
        :type value: int
        :return: état en cours. 0 = halt, 1 = en cours, 2 = input attendu.
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
            # la suite va dépendre de l'instruction :
            #     halt ramène currentState à 0 et return 0
            #     store ou load chargent l'adresse cible dans le registre d'adresse mémoire
            #     calculs placent les entrées de l'UAL et demandent calcul, up de __currentState
            #     move fait transfert direct et termine, donc retour __currentState à 0, return 1
            #     saut charge (ou pas selon si conditionnel) l'adresse cible dans pointeur de ligne puis retour __currentState à 0, return 1
            #     print charge le registre dans la pile Print puis retour __currentState à 0, return 1
            #     input place le flag __waitingInput à True, up de __currentState et return 3
            pass

        if __currentState == 3
            # N'arrive que dans certains cas. Voir la suite dans ces cas là.
            pass

        # bien sûr aménagement possible :
        # return global ? ou return au détail ?
        # up de __currentState dans chaque cas ou un up à la toute fin ?(le même pour tous les cas)
        # etc.




