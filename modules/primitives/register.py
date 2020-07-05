"""
.. module:: register
:synopsis: objet représentant un registre ainsi que les conteneurs de ces registres
"""

from typing import Union, List, Optional

class Register:
    _rang   :int  = 0
    _free   :bool = True
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

    def setFree(self):
        self._free = True

    def unsetFree(self):
        self._free = False

    @property
    def free(self):
        """Accesseur
        :return: Le registre est inoccupé
        :rtype: bool
        """

        return self._free

    @property
    def isTemp(self):
        """Accesseur
        :return: Le registre est élément de mémoire temporaire
        :rtype: bool
        """

        return self._isTemp


class RegisterBank:
    _registers: List[Register]
    _size: int
    def __init__(self, size:int):
        assert size > 1
        self._registers = [Register(i, False) for i in range(size)]
        self._size = size

    def getFreeRegister(self) -> Optional[Register]:
        """
        :result: premier registre libre, en partant du rang le plus élevé
        :rtype: Optional[Register]
        """
        freeRegister = [r for r in self._registers if r.free]
        if len(freeRegister) == 0:
            return None
        return freeRegister[-1]

    def hasAvailables(self) -> bool:
        """
        :return: y a-t-il des registres libres ?
        :rtype: bool
        """
        return len([r for r in self._registers if r.free]) > 0

    def isFree(self, index:int) -> bool:
        """
        :param index: indice du registre cherché
        :type index: int
        :return: le registre est-il libre ?
        :rtype: bool
        """
        assert 0 <= index < len(self._registers)
        return self._registers[index].free

    def getZeroRegister(self) -> Register:
        """
        :return: le registre d'indice 0
        :rtype: Register
        """
        return self._registers[0]

class RegistersStack:
    _registers: List[Register]
    def __init__(self):
        self._registers = []

    def readTop(self) -> Optional[Register]:
        """
        :return: registre au sommet de la pile, sans le libérer.
        :rtype: Optional[Register]
        :raises: CompilationError s'il n'y a pas d'opérande dans la pile
        .. note:: si le numéro est ``< 0``, provoque le dépilage d'un item de mémoire et retour du numéro de registre ayant accueilli le retour.
        """
        if len(self._registers) == 0:
            return None
        return self._registers[-1]

    def pop(self) -> Optional[Register]:
        """
        retourne le sommet de la pile et le libère
        :return: sommet de la pile
        :rtype: Optional[Register]
        """
        if len(self._registers) == 0:
            return None
        register = self._registers.pop()
        register.setFree()
        return register

    def push(self, register:Register):
        """
        :param register: Registre ajouter sur la pile
        :type register: Register
        """
        register.unsetFree()
        self._registers.append(register)

    def extract(self, index:int) -> Optional[Register]:
        """
        retourne l'élément à l'indice index et le libère

        :param index: indice à extraire
        :type index:int
        :return: bas de la pile
        :rtype: Optional[Register]
        """
        if not(0 <= index < len(self._registers)):
            return None
        register = self._registers[index]
        register.setFree()
        del self._registers[index]
        return register

    def insert(self, index:int, register:Register):
        """
        :param index: indice à insérrer
        :type index:int
        :param register: Registre ajouter en bas de la pile
        :type register: Register
        """
        assert 0 <= index <= len(self._registers)
        register.unsetFree()
        self._registers.insert(index, register)

    def swap(self):
        """
        permute les 2 registres au sommet
        """
        if len(self._registers) <= 1:
            return
        self._registers[-1], self._registers[-2] = self._registers[-2], self._registers[-1]

    def getLastRegisterIndex(self) -> int:
        """
        :return: indice du registre (pas temp) le plus bas dans la pile
        :rtype: int
        """
        l = [i for i, r in enumerate(self._registers) if not r.isTemp]
        if len(l) == 0:
            return -1
        return l[0]

    def index(self, register:Register) -> int:
        """
        :param register: Registre cherché
        :type register: Register
        :return: indice du registre ou -1
        :rtype:int
        """
        if register in self._registers:
            return self._registers.index(register)
        return -1

    def __str__(self) -> str:
        """transtypage
        :return: version string
        :rtype: str
        """
        return "\n".join([str(it) for it in self._registers])

class TempMemoryStack:
    _registers: List[Register]
    def __init__(self):
        self._registers = []

    def getFreeRegister(self) -> Register:
        """
        :return: première mémoire libre. La crée au besoin
        :rtype: Register
        """
        f = [r for r in self._registers if r.free]
        if len(f) > 0:
            return f[0]
        r = Register(len(self._registers), True)
        self._registers.append(r)
        return r


