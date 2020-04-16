"""
.. module:: executeurcomponents
:synopsis: Classes définissant le fonctionnement des organes de l'exécuteur.
    Mémoire, registres, UAL, écran...
"""

from typing import List, Union, Callable, Tuple, Dict, Optional, Any, cast

class DataValue:
    """Gestion d'un mot de donnée, en particulier

    * taille du mot
    * gestion de dépassemnt
    * affichage dans différentes bases
    * calculs
    """
    def __init__(self, size:int, value:int=0):
        '''
        :param size: taille du mot
        :type size: int
        :param value: valeur initiale
        :type value: int
        '''
        self._size = size
        self._mask = 2**size - 1
        self._negMask = 2**(size-1)
        self._value = value & self._mask
        self._binFormat = "0b{:0"+str(size)+"b}"
        if size % 4 > 0:
            self._hexFormat = "0x{:0"+str(size//4 + 1)+"X}"
        else:
            self._hexFormat = "0x{:0"+str(size//4)+"X}"

    @property
    def intValue(self) -> int:
        return self._value

    def toSignInt(self) -> int:
        '''transtypage en int tenant compte de l'éventel signe CA2

        :return: valeur courante
        :rtype: int
        '''
        if self.isPos():
            return self._value
        return - (((~self._value) + 1) & self._mask)

    def isNul(self) -> bool:
        '''test si c'est entier nul

        :result: la valeur est nulle
        :rtype: bool
        '''
        return self._value == 0

    def isPos(self) -> bool:
        '''test si c'est entier est positif (en CA2, tenant compte de la base)

        :result: la valeur est positive (ou nulle)
        :rtype: bool
        '''
        return self._value & self._negMask == 0

    def inc(self) -> None:
        '''incrémente la valeur tenant compte du codage CA2
        '''
        self._value = (self._value + 1) & self._mask

    def opposite(self) -> "DataValue":
        '''calcul l'opposé d'un entier tenant compte du codage CA2

        :return: oppposé de la valeur
        :rtype: DataValue
        '''
        oppValue = ((~self._value) + 1) & self._mask
        return DataValue(self._size, oppValue)

    def inverse(self) -> "DataValue":
        '''calcul l'inverse d'un entier tenant compte du codage CA2

        :return: inverse de la valeur
        :rtype: DataValue
        '''
        return DataValue(self._size, ~self._value)

    def mask(self, mask:int) -> "DataValue":
        '''Calcule le résultat de la valeur masquée

        :param mask: masque
        :type mask: int
        :return: valeur masquée
        :rtype: DataValue
        '''
        return DataValue(self._size, self._value & mask)

    def toStr(self, base:str = 'bin') -> str:
        '''transtypage tenant compte que value n'est pas forcément sur 32 bits
        comme les int ordinaire de python pour lesquels str() est conçu

        :param base: base de l'écriture parmi 'bin', 'hex', 'dec', 'udec'
        :type base: str
        :result: valeur sous forme str
        :rtype: str
        '''
        if base == 'bin':
            return self._binFormat.format(self._value)
        if base == 'hex':
            return self._hexFormat.format(self._value)
        if base == 'udec' or self.isPos():
            # décimal non signé
            return str(self._value)
        # pour base 10, on ajoute une notation avec - pour nombre négatif
        # dans ce cas, il faut tenir compte du codage CA2 avec une taille
        # de mot qui n'est pas forcément le 32 bits de python
        return "-"+str(((~self._value) + 1) & self._mask)

    def calc(self, otherValue:"DataValue", operation:str) -> "DataValue":
        '''calcule l'opération avec une autre valeur

        :param otherValue: autre valeur
        :type otherValue: DataValue
        :return: résultat
        :rtype: DataValue
        '''
        if operation == "&":
            return DataValue(self._size, self._value & otherValue._value)
        if operation == "|":
            return DataValue(self._size, self._value | otherValue._value)
        if operation == "^":
            return DataValue(self._size, self._value ^ otherValue._value)
        if operation == "-":
            return self.calc(otherValue.opposite(), "+")
        if operation == "*":
            result = self.toSignInt() * otherValue.toSignInt()
            return DataValue(self._size, result)
        if operation == "/":
            result = self.toSignInt() // otherValue.toSignInt()
            return DataValue(self._size, result)
        if operation == "%":
            result = self.toSignInt() % otherValue.toSignInt()
            return DataValue(self._size, result)

        return DataValue(self._size, self._value + otherValue._value)

    def clone(self) -> "DataValue":
        return DataValue(self._size, self._value)

    def __str__(self) -> str:
        '''transtypage str, par défaut en binaire
        '''
        return self.toStr()

class BaseComponent:
    """Composant de base définissant les propriétés élémentaires,
    en particulier les propriétées liées aux événements
    """

    __onEvent:List[Tuple[str,Callable[[Dict[str, Any]],None]]]
    def __init__(self, size:int):
        '''
        :param size: taille des mots en bits
        :type size: int
        '''
        self._size = size
        self.__onEvent = []

    @property
    def size(self) -> int:
        '''Accesseur

        :return: taille d'un mot de données
        :rtype: int
        '''
        return self._size

    def bind(self, eventName:str, callback:Callable[[Dict[str,Union[str,int]]],None]):
        '''Enregistre un événement

        :param eventName: nom de l'événement
        :type eventName: str
        :param callback: fonction callback
        :type callback: Callable
        '''
        self.__onEvent.append((eventName, callback))

    def trigger(self, eventName:str, params:Dict[str, Any]) -> None:
        '''Déclenche un événement

        :param eventName: nom de l'événement
        :type eventName: str
        :param params: paramètres empaquetés
        :type params: Union[str,int]
        '''
        eventName = "on"+eventName
        for evt, callback in self.__onEvent:
            if evt == eventName:
                callback(params)

class BufferComponent(BaseComponent):
    """
    Gestion du buffer d'entrée
    """
    _list:List[DataValue]

    def __init__(self, size:int):
        super().__init__(size)
        self._list = []

    def empty(self) -> bool:
        '''
        :return: True si le buffer est vide
        :rtype: bool
        '''
        return len(self._list) == 0

    def read(self) -> Union[DataValue, bool]:
        '''
        :return: premier item du buffer s'il existe, sinon False
        :rtype: Union(DataValue, bool)

        .. note:: déclenche l'événement "readempty"
        ou "read" renvoyant la valeur "readed"
        '''
        if len(self._list) > 0:
            out = self._list.pop(0)
            self.trigger("read", { "readed": out })
            return out
        self.trigger("readempty", {})
        return False

    def write(self, value:int) -> None:
        '''
        :param value: valeur à ajouter dans le buffer
        :type value: int

        .. note:: déclenche l'événement "write" renvoyant "writed"
        '''
        newValue = DataValue(self._size, value)
        self._list.append(newValue)
        self.trigger("write", { "writed": newValue })

    @property
    def list(self):
        '''Accesseur
        :return: clone du contenu du buffer
        :rtype: List[int]
        '''
        return [item for item in self._list]

class ScreenComponent(BaseComponent):
    """
    Gestion de l'écran
    """
    _list:List[DataValue]

    def __init__(self, size):
        super().__init__(size)
        self._list = []

    def empty(self) -> bool:
        '''
        :return: True si le buffer est vide
        :rtype: bool
        '''
        return len(self._list) == 0

    def getStringList(self, base:str = 'bin') -> List[str]:
        '''
        :param base: base de la lecture, parmi 'bin', 'dec', 'hex', 'udec'
        :type base: str
        :return: liste du contenu de l'écran
        :rtype: List[str]
        '''
        return [item.toStr(base) for item in self._list]

    def clear(self):
        '''Efface le contenu

        .. note:: déclenche l'événement "clear"
        '''
        self._list = []
        self.trigger("clear", {})

    def write(self, value:Union[DataValue,int]) -> None:
        '''
        :param value: ajoute valeur à l'écran
        :type value: Union[DataValue,int]

        .. note:: déclenche l'événement "write" renvoyant "writed"
        '''
        if isinstance(value,int):
            value = DataValue(self._size, value)
        self._list.append(value)
        self.trigger("write", { "writed":value.clone() })

class UalComponent(BaseComponent):
    '''
    Gestion de l'Unité Arithmétique et Logique
    '''
    __result:DataValue
    __op1:DataValue
    __op2:DataValue
    __isZero:bool = True
    __isPos:bool = True
    __operation:str = "+"
    def __init__(self, size:int):
        super().__init__(size)
        self.__op1 = DataValue(size, 0)
        self.__op2 = DataValue(size, 0)
        self.__result = DataValue(size, 0)

    @property
    def operation(self) -> str:
        '''Accesseur

        :return: opération en cours
        :rtype: str
        '''
        return self.__operation

    @property
    def op1(self) -> DataValue:
        '''Accesseur

        :return: opérande 1
        :rtype: DataValue
        '''
        return self.__op1.clone()

    @property
    def op2(self) -> DataValue:
        '''Accesseur

        :return: opérande 2
        :rtype: DataValue
        '''

        return self.__op2.clone()

    def setOperation(self, opName:str) -> None:
        '''Fixe l'opération

        :param opName: opération parmi neg, ~, +, -, *, /, %, &, |, ^
        :type opName: str

        .. note:: déclenche l'événement "setoperation" renvoyant "operation"
        '''
        if opName in ("neg", "~", "+", "-", "*", "/", "%", "&", "|", "^", "cmp"):
            self.__operation = opName
            self.trigger("setoperation", { "operation":opName })

    def writeFirstOperand(self, value:Union[DataValue,int]) -> None:
        '''Fixe l'opérande 1

        :param value: valeur de l'opérande
        :type value: Union[DataValue,int]

        .. note:: déclenche l'événement "writeop1" renvoyant "writed"
        '''
        if isinstance(value,int):
            value = DataValue(self._size, value)
        self.__op1 = value
        self.trigger("writeop1", { "writed": value.clone()})

    def writeSecondOperand(self, value:Union[DataValue,int]) -> None:
        '''Fixe l'opérande 2

        :param value: valeur de l'opérande
        :type value: Union[DataValue,int]

        .. note:: déclenche l'événement "writeop2" renvoyant "writed"
        '''
        if isinstance(value,int):
            value = DataValue(self._size, value)
        self.__op2 = value
        self.trigger("writeop2", { "writed": value.clone()})

    def read(self) -> DataValue:
        '''lit le résultat

        :return: résultat du dernier calcul
        :rtype: DataValue
        '''
        return self.__result.clone()

    def execCalc(self) -> DataValue:
        '''exécute le calcul

        :return: valeur du résultat
        :rtype: DataValue
        '''
        if self.__operation == "~":
            result = self.__op1.inverse()
        elif self.__operation == "neg":
            result = self.__op1.opposite()
        elif self.__operation == "cmp":
            result = self.__op1.calc(self.__op2, "-")
        else:
            result = self.__op1.calc(self.__op2, self.__operation)
        self.__isPos = result.isPos()
        self.__isZero = result.isNul()
        self.trigger("calc", { "result":result.clone(), "iszero":self.__isZero, "ispos":self.__isPos } )
        if self.__operation != "cmp":
            self.__result = result
        return result

    @property
    def isZero(self) -> bool:
        '''Prédicat

        :return: le résultat de la dernière opération est nul
        :rtype: bool
        '''
        return self.__isZero

    @property
    def isPos(self) -> bool:
        '''Prédicat

        :return: le résultat de la dernière opération est positif ou nul
        :rtype: bool
        '''
        return self.__isPos



class RegisterComponent(BaseComponent):
    """
    Gestion d'un registre isolé
    """
    _value:DataValue
    _name:str

    def __init__(self, name:str, size:int):
        super().__init__(size)
        self._value = DataValue(size)
        self._name = name

    @property
    def name(self) -> str:
        '''Accesseur

        :return: nom du registre
        :rtype: str
        '''
        return self._name

    @property
    def intValue(self) -> int:
        '''Accesseur

        :return: valeur entière du registre
        :rtype: int
        '''
        return self._value.intValue

    def inc(self) -> None:
        '''incrémente la valeur du registre.

        .. note:: déclenche l'événement "inc" renvoyant "writed"
        '''
        self._value.inc()
        self.trigger("inc", { "writed":self._value.clone() })

    def read(self) -> DataValue:
        '''lecture de value

        :return: valeur courante du registre
        :rtype: int
        '''
        return self._value.clone()

    def write(self, value:Union[DataValue,int]) -> None:
        ''' écrit la valeur dans le registre

        :param value: ajoute valeur à l'écran
        :type value: Union[DataValue,int]

        .. note:: déclenche l'événement "write" renvoyant "writed"
        '''
        if isinstance(value,int):
            value = DataValue(self._size, value)
        self._value = value
        self.trigger("write", { "writed":self._value.clone() })

class RegisterGroup(BaseComponent):
    """
    Gestion d'un banc de registres. Le nombre de registre peut être limité à la création
    ou illimité (écrire à une adresse hors limite augmente la taille)
    """
    _list: List[DataValue]
    _unlimited: bool

    def __init__(self, registerNumber:int, size:int, initialValues:List[int]=[]):
        '''
        :param registerNumber: nombre de cellule mémoire. 0 si illimité
        :type registerNumber: int
        :param size: taille des mots de données
        :type size: int
        '''
        super().__init__(size)
        self._unlimited = (registerNumber == 0)
        if registerNumber == 0:
            self._list = [DataValue(size, item) for item in initialValues]
        else:
            loaded = [DataValue(size, item) for item in initialValues[:registerNumber]]
            leftToInit = [DataValue(size) for item in range(registerNumber-len(loaded))]
            self._list = loaded + leftToInit

    @property
    def content(self) -> List[DataValue]:
        '''Accesseur

        :return: liste des valeurs contenues dans les registres
        :rtype: List[DataValue]
        '''
        return [item.clone() for item in self._list]

    def __fill(self, index) -> None:
        '''Complète la mémoire pour que l'indice index soit défini
        si le nombre de registres est illimité

        :param index: indice à atteindre
        :type index: int

        .. note:: déclenche l'événement "fill"
        '''
        filled = False
        while len(self._list) <= index:
            filled = True
            self._list.append(DataValue(self._size))
        if filled:
            self.trigger("fill", {})

    def inc(self, index:int) -> None:
        '''incrémente la valeur du registre

        :param index: indice du registre incrémenté
        :type index: int

        .. note:: déclenche l'événement "inc" qui renvoie "index" et "value"
        '''
        if self._unlimited and index > len(self._list):
            self.__fill(index)
        if 0 <= index < len(self._list):
            value = self._list[index]
            value.inc()
            self.trigger("inc", {"value": value.clone(), "index":index} )

    def read(self, index:int) -> Optional[DataValue]:
        '''lecture de la valeur du registre d'index n
        :param index: indice du registre lu
        :type index: int
        :return: valeur courante du registre. -1 par défaut
        :rtype: int

        .. note:: déclenche l'événement "read" qui renvoie "index" et "value"
        '''
        if self._unlimited and index > len(self._list):
            self.__fill(index)
        if 0 <= index < len(self._list):
            value = self._list[index].clone()
            self.trigger("read", {"value": value, "index":index} )
            return value
        return None

    def write(self, index:int, value:Union[DataValue,int]) -> None:
        ''' écrit la valeur dans le registre

        :param index: indice du registre écrit
        :type index: int
        :param value: écrit la valeur dans le registre
        :type value: Union[DataValue,int]

        .. note:: déclenche l'événement "write" qui renvoie "index" et "writed"
        '''
        if isinstance(value, int):
            value = DataValue(self.size, value)
        if self._unlimited and index > len(self._list):
            self.__fill(index)
        if 0 <= index < len(self._list):
            self._list[index] = value
            self.trigger("write", { "writed":value, "index":index })


class MemoryComponent(RegisterGroup):
    """
    Gestion de la mémoire
    extension de RegisterGroup avec adresseRegister en plus
    et nombre de registres illimités (limité par la taille de l'adresse)
    """
    __addressRegister: RegisterComponent
    def __init__(self, size:int, initialValues:List[Union[int,str]]=[]):
        self.__addressRegister = RegisterComponent("Registre d'adresse", size)
        memory = []
        for index, item in enumerate(initialValues):
            if isinstance(item,str):
                memory.append(int(item,2))
            else:
                memory.append(item)
        super().__init__(0, size, memory)

    def incAddressedRegister(self) -> None:
        '''Incrémente le registre à l'adresse sélectionnée
        par le registre d'adresse
        '''
        address = self.__addressRegister.intValue
        super().inc(address)

    def readAddressedRegister(self) -> DataValue:
        '''Lit le registre à l'adresse sélectionnée
        par le registre d'adresse

        :return: valeur contenue dans le registre
        :rtype: DataValue
        '''
        address = self.__addressRegister.intValue
        readed = super().read(address)
        return cast(DataValue, readed)

    def writeAddressedRegister(self, value:Union[DataValue,int]) -> None:
        '''Écrit dans le registre à l'adresse sélectionnée
        par le registre d'adresse

        :param value: valeur à écrire
        :rtype: Union[DataValue,int]
        '''
        if isinstance(value, int):
            value = DataValue(self.size, value)
        address = self.__addressRegister.intValue
        super().write(address, value)

    def setAddress(self, value:Union[DataValue,int]) -> None:
        '''Écrit dans le registre d'adresse

        :param value: nouvelle adresse
        :rtype: Union[DataValue,int]

        .. note:: déclenche l'événement "writeaddress" qui renvoie "address"
        '''
        if isinstance(value, int):
            value = DataValue(self.size, value)
        self.__addressRegister.write(value)
        self.trigger("writeaddress", {"address": value.clone()})

    @property
    def address(self):
        '''Accesseur

        :return: valeur de l'adresse courante
        :rtype: DataValue
        '''
        return self.__addressRegister.read()

