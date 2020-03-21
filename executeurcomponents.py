"""
.. module:: executeurcomponents
   :synopsis: classes composants les organes de l'exécuteur
"""

from typing import List, Union, Callable, Tuple, Dict

class BaseComponent:
    __onEvent:List[Tuple[str,Callable[[Dict[str,Union[str,int]]],None]]]
    def __init__(self):
        self.__onEvent = []

    def bind(self, eventName:str, callback:Callable[[Dict[str,Union[str,int]]],None]):
        '''Enregistre un événement

        :param eventName: nom de l'événement
        :type eventName: str
        :param callback: fonction callback
        :type callback: Callable
        '''
        self.__onEvent.append((eventName, callback))

    def trigger(self, eventName:str, params:Dict[str,Union[str,int]]) -> None:
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

class Buffer(BaseComponent):
    """
    Gestion du buffer d'entrée
    """
    __list:List[int]

    def __init__(self):
        super().__init__()
        self.__list = []

    def empty(self) -> bool:
        '''
        :return: True si le buffer est vide
        :rtype: bool
        '''
        return len(self.__list) == 0

    def read(self) -> Union[int, bool]:
        '''
        :return: premier item du buffer s'il existe, sinon False
        :rtype: Union(int, bool)
        '''
        if len(self.__list) > 0:
            out = self.__list.pop(0)
            self.trigger("read", { "readed": out})
            return out
        self.trigger("readempty", {})
        return False

    def write(self, value:int) -> None:
        '''
        :param value: valeur à ajouter dans le buffer
        :type value: int
        '''
        self.__list.append(value)
        self.trigger("write", { "writed": value })



    @property
    def list(self):
        '''Accesseur
        :return: clone du contenu du buffer
        :rtype: List[int]
        '''
        return [item for item in self.__list]

class Screen(BaseComponent):
    """
    Gestion de l'écran
    """
    __list:List[str]

    def __init__(self):
        super().__init__()
        self.__list = []

    def empty(self) -> bool:
        '''
        :return: True si le buffer est vide
        :rtype: bool
        '''
        return len(self.__list) == 0

    def read(self) -> List[str]:
        '''
        :return: liste du contenu de l'écran
        :rtype: List[str]
        '''
        return [item for item in self.__list]

    def clear(self):
        '''Efface le contenu
        '''
        self.__list = []
        self.trigger("clear", {})

    def write(self, value:int) -> None:
        '''
        :param value: ajoute valeur à l'écran
        :type value: int
        '''
        self.__list.append(str(value))
        self.trigger("write", { "writed":value })

class Register(BaseComponent):
    """
    Gestion d'un registre
    """
    __value:int = 0
    __name:str
    __mask:int

    def __init__(self, name:str, size:int):
        super().__init__()
        self.__name = name
        self.__mask = 2**size-1

    @property
    def name(self) -> str:
        '''Accesseur

        :return: nom du registre
        :rtype: str
        '''
        return self.__name

    def inc(self) -> int:
        """incrémente la valeur du registre"""
        self.__value += 1
        self.__value &= self.__mask
        self.trigger("inc", {"value": self.__value})
        return self.__value

    def read(self) -> int:
        '''lecture de value

        :return: valeur courante du registre
        :rtype: int
        '''
        return self.__value

    def write(self, value:int) -> None:
        ''' écrit la valeur dans le registre

        :param value: ajoute valeur à l'écran
        :type value: int
        '''
        self.__value = value & self.__mask
        self.trigger("write", { "writed":self.__value })

class RegisterGroup(BaseComponent):
    """
    Gestion d'un groupe de registres
    """
    __registerNumber:int = 0
    __list: List[Register]

    def __init__(self, registerNumber:int, size:int):
        super().__init__()
        self.__list = [Register("", size) for i in range(registerNumber)]

    def inc(self, index:int) -> int:
        '''incrémente la valeur du registre

        :param index: indice du registre incrémenté
        :type index: int
        :return: nouvelle valeur du registre, -1 par défaut
        :rtype: int
        '''
        if 0 <= index < self.__registerNumber:
            newValue = self.__list[index].inc()
            self.trigger("inc", {"value": newValue} )
            return newValue
        return -1

    def read(self, index:int) -> int:
        '''lecture de la valeur du registre d'index n
        :param index: indice du registre lu
        :type index: int
        :return: valeur courante du registre. -1 par défaut
        :rtype: int
        '''
        if 0 <= index < self.__registerNumber:
            return self.__list[index].read()
        return -1

    def write(self, index:int, value:int) -> None:
        ''' écrit la valeur dans le registre

        :param index: indice du registre écrit
        :type index: int
        :param value: ajoute valeur à l'écran
        :type value: int
        '''
        if 0 <= index < self.__registerNumber:
            self.__list[index].write(value)
            self.trigger("write", { "writed":self.__list[index].read() })
