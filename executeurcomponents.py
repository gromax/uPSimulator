"""
.. module:: executeurcomponents
   :synopsis: classes composants les organes de l'exécuteur
"""

from typing import List, Union, Callable, Tuple

class Buffer:
    """
    Gestion du buffer d'entrée
    """
    __list:List[int]
    __onEvent:List[Tuple[str,Callable[[],None]]]

    def __init__(self):
        self.__list = []
        self.__onEvent = []

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
            for eventName, callback in self.__onEvent:
                if eventName == "onread":
                    callback()
            return out
        for eventName, callback in self.__onEvent:
            if eventName == "onreadempty":
                callback()
        return False

    def write(self, value:int) -> None:
        '''
        :param value: valeur à ajouter dans le buffer
        :type value: int
        '''
        self.__list.append(value)
        for eventName, callback in self.__onEvent:
            if eventName == "onwrite":
                callback()

    def bind(self, eventName:str, callback:Callable[[],None]):
        if eventName in ("onread", "onwrite", "onreadempty"):
            self.__onEvent.append((eventName, callback))

    @property
    def list(self):
        '''Accesseur
        :return: clone du contenu du buffer
        :rtype: List[int]
        '''
        return [item for item in self.__list]

