"""
.. module:: variable
   :synopsis: définition d'un objet contenant une variable mémoire
"""

from errors import *

class Variable:
    def __init__(self, nom:str, value:int = 0):
        """Constructeur de la classe

        :param nom: nom de la variable
        :type nom: str
        :param value: valeur initiale. 0 par défaut
        :type value: int
        """
        self.__nom = nom
        self.__value = value

    def getName(self) -> str:
        """Retourne le nom de la variable : attribut __name

        :return: nom de la variable
        :rtype: str

        :Example:
            >>> Variable("x").getName()
            'x'

        .. warning:: Il est possible que l'on crée plusieurs variables pour un même nom
        """

        return self.__nom

    def __str__(self) -> 'str':
        """Transtypage -> str. Affiche le nom de la variable préfixé par @

        :return: @ + nom de la variable
        :rtype: str

        :Example:
            >>> str(Variable("x"))
            '@x'

        """

        return "@"+self.__nom

    def getValueBinary(self, wordSize:int) -> 'str':
        """Retourne chaîne de caractère représentant le code CA2 de self.__value,
        pour un mot de taille wordSize bits

        :param wordSize: taille du mot binaire
        :type wordSize: int
        :return: code CA2 de la valeur initiale de la variable, sur wordSize bits
        :rtype: str

        :Example:
            >>> Variable("x",45).getValueBinary(8)
            '00101101'

            >>> Variable("x",-45).getValueBinary(8)
            '11010011'

            >>> Variable("x",1000).getValueBinary(8)
            Traceback (most recent call last):
            ...
            errors.CompilationError: @x : Variable de valeur trop grande !
        """

        if self.__value < 0:
            # utilise le CA2
            valueToCode = (~(-self.__value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self.__value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize or self.__value > 0 and outStr[1] == '1':
            raise CompilationError(f"{self} : Variable de valeur trop grande !")
        return outStr

    def getValue(self) -> int:
        """Retourne la valeur initiale de la variable

        :return: valeur initiale de la variable
        :rtype: int

        :Example:
            >>> Variable("x").getValue()
            0

            >>> Variable("x",15).getValue()
            15

        """
        return self.__value
