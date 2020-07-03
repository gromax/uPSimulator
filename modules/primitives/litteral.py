"""
.. module:: litteral
   :synopsis: définition d'un objet contenant une valeur littérale
"""

class Litteral:
    def __init__(self, value: int):
        """Constructeur de la classe

        :param value: valeur du littéral
        :type value: int
        """
        assert isinstance(value,int)
        self._value = value

    @property
    def value(self) -> int:
        """Retourne la valeur du littéral

        :return: valeur du littéral
        :rtype: int

        :Example:
            >>> Litteral(8).value
            8
            >>> Litteral(-15).value
            -15
        """

        return self._value

    def negClone(self) -> 'Litteral':
        """Produit un clone du littéral avec valeur opposée

        :return: clone du littéral avec valeur opposée
        :rtype: Litteral

        :Example:
            >>> Litteral(8).negClone().value
            -8
        """

        return Litteral(-self._value)

    def isBetween(self, minValue:int, maxValue:int) -> bool:
        """Retourne True si la valeur courante est comprise entre minValue et maxValue.

        :param minValue: valeur minimum
        :type minValue: int
        :param maxValue: valeur maximum
        :type maxValue: int
        :return: Vrai si la valeur du littéral est compris entre minValue et maxValue, inclus
        :rtype: bool

        :Example:
            >>> Litteral(8).isBetween(4,12)
            True
            >>> Litteral(25).isBetween(4,12)
            False

        """

        return minValue <= self._value <= maxValue

    def bitMinSize(self) -> int:
        """Nombre de bits minimum pour coder un tel nombre
        :return: nombre de bits
        :rtype: int

        :Example:
            >>> Litteral(45).bitMinSize()
            6
        """
        if self._value == 0:
            return 1
        posValue = abs(self._value)
        n = 0
        while posValue > 0:
            posValue = posValue // 2
            n += 1
        if self._value < 0:
            return n + 1
        return n

    def __str__(self) -> str:
        """Transtypage -> str. Affiche le littéral préfixé par #

        :return: # + valeur du littéral
        :rtype: str

        :Example:
            >>> str(Litteral(8))
            '#8'

        """
        return "#"+str(self._value)

if __name__=="__main__":
    import doctest
    doctest.testmod()
