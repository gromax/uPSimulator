"""
.. module:: register
:synopsis: objet représentant un registre ainsi que les conteneurs de ces registres
"""

from typing import Union, List, Optional

class Register:
    _rang   :int  = 0
    _isTemp :bool = False
    def __init__(self, rang:int, isTemp:bool):
        self._rang = rang
        self._isTemp = isTemp

    def __str__(self) -> str:
        """Transtypage

        :result: représentation en châine de texte
        :rtype: str

        :Example:

        >>> r = Register(2,False)
        >>> str(r)
        'r2'
        """
        if self._isTemp:
            return "_m{}".format(self._rang)
        return "r{}".format(self._rang)

    @property
    def isTemp(self) -> bool:
        """Accesseur
        :return: Le registre est élément de mémoire temporaire
        :rtype: bool
        """

        return self._isTemp

    @property
    def rank(self) -> int:
        """Accesseur
        :return: rang du registre
        :rtype: int
        """

        return self._rang

class RegistersManager:
    _stack: List[Register]
    _bank : List[Register]
    _temp : List[Register]
    _size : int

    def __init__(self, size:int):
        """Constructeur

        :param size: nombre de registres
        :type size: int
        """
        assert size > 1
        self._stack = []
        self._temp = []
        self._bank = [Register(i, False) for i in range(size)]
        self._size = size

    def purgeStack(self):
        """Vide la pile
        """
        self._stack = []

    def readTopStack(self) -> Optional[Register]:
        """
        :return: registre au sommet de la pile, sans le libérer.
        :rtype: Optional[Register]
        :raises: CompilationError s'il n'y a pas d'opérande dans la pile
        .. note:: si le numéro est ``< 0``, provoque le dépilage d'un item de mémoire et retour du numéro de registre ayant accueilli le retour.
        """
        if len(self._stack) == 0:
            return None
        return self._stack[-1]

    def pop(self) -> Optional[Register]:
        """
        retourne le sommet de la pile et le libère
        :return: sommet de la pile
        :rtype: Optional[Register]
        """
        if len(self._stack) == 0:
            return None
        register = self._stack.pop()
        return register

    def push(self, register:Register):
        """
        :param register: Registre ajouter sur la pile
        :type register: Register
        """
        self._stack.append(register)

    def extractFromStack(self, index:int) -> Optional[Register]:
        """
        retourne l'élément à l'indice index et le libère

        :param index: indice à extraire
        :type index:int
        :return: bas de la pile
        :rtype: Optional[Register]
        """
        if not(0 <= index < len(self._stack)):
            return None
        register = self._stack[index]
        del self._stack[index]
        return register

    def insertInStack(self, index:int, register:Register):
        """
        :param index: indice à insérrer
        :type index:int
        :param register: Registre ajouter en bas de la pile
        :type register: Register
        """
        assert 0 <= index <= len(self._stack)
        self._stack.insert(index, register)

    def swap(self):
        """
        permute les 2 registres au sommet de la pile
        """
        if len(self._stack) <= 1:
            return
        self._stack[-1], self._stack[-2] = self._stack[-2], self._stack[-1]

    def getLastRegisterIndexInStack(self) -> int:
        """
        :return: indice du registre (pas temp) le plus bas dans la pile
        :rtype: int
        """
        l = [i for i, r in enumerate(self._stack) if not r.isTemp]
        if len(l) == 0:
            return -1
        return l[0]

    def indexInStack(self, register:Register) -> int:
        """
        :param register: Registre cherché
        :type register: Register
        :return: indice dans la pile du registre ou -1
        :rtype:int
        """
        if register in self._stack:
            return self._stack.index(register)
        return -1

    def getFreeRegister(self) -> Optional[Register]:
        """
        :result: premier registre libre, en partant du rang le plus élevé
        :rtype: Optional[Register]
        """
        freeRegister = [r for r in self._bank if not r in self._stack]
        if len(freeRegister) == 0:
            return None
        return freeRegister[-1]

    def hasAvailables(self) -> bool:
        """
        :return: y a-t-il des registres libres ?
        :rtype: bool
        """
        return len([r for r in self._bank if not r in self._stack]) > 0

    def isFree(self, index:int) -> bool:
        """
        :param index: indice du registre cherché
        :type index: int
        :return: le registre est-il libre ?
        :rtype: bool
        """
        assert 0 <= index < len(self._bank)
        register = self._bank[index]
        return not register in self._stack

    def getZeroRegister(self) -> Register:
        """
        :return: le registre d'indice 0
        :rtype: Register
        """
        return self._bank[0]

    def getFreeTempRegister(self) -> Register:
        """
        :return: première mémoire libre. La crée au besoin
        :rtype: Register
        """
        f = [r for r in self._temp if not r in self._stack]
        if len(f) > 0:
            return f[0]
        r = Register(len(self._temp), True)
        self._temp.append(r)
        return r
