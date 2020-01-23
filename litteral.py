"""
.. module:: litteral
   :platform: Unix, Windows
   :synopsis: définition d'un objet contenant une valeur littérale
"""

class Litteral:
    def __init__(self, value: int):
        '''
        value = int
        '''
        assert isinstance(value,int)
        self.__value = value

    def clone(self) -> 'Litteral':
        return Litteral(self.__value)

    def negClone(self) -> 'Litteral':
        return Litteral(-self.__value)

    def isBetween(self, minValue:int, maxValue:int) -> bool:
        """Retourne True si la valeur courante est comprise entre minValue et maxValue.
        Args:
           minValue (int): valeur minimum
           maxValue (int): valeur maximum

        Returns:
           bool.  The return code::

              True -- La valeur est dans [minValue ; maxValue]
              False -- La valeur n'est pas dans [minValue ; maxValue]

        >>> Litteral(8).isBetween(4,12)
        True

        >>> Litteral(25).isBetween(4,12)
        False

        """

        return minValue <= self.__value <= maxValue

    def getValue(self) -> int:
        return self.__value

    def __str__(self) -> str:
        return "#"+str(self.__value)
