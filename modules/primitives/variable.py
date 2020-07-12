"""
.. module:: variable
   :synopsis: définition d'un objet contenant une variable mémoire
"""

from typing import Dict
from modules.errors import CompilationError

class Variable:
    _value:int = 0
    def __init__(self, nom:str):
        """Constructeur de la classe

        :param nom: nom de la variable
        :type nom: str
        """
        self._name = nom

    @staticmethod
    def toInt(name:str) -> int:
        """Déduit la valeur à partir du nom préfixé de @
        :param name: nom de la variable
        :type name: str
        :return: valeur initiale de la variable
        :rtype: int
        """
        if len(name) <= 2 or name[1] != "#":
            return 0
        signe = 1
        if name[2] == "m":
            strValue = name[3:]
            signe = -1
        else:
            strValue = name[2:]
        return signe * int(strValue)

    @staticmethod
    def binary(name:str, wordSize:int) -> 'str':
        """Retourne chaîne de caractère représentant le code CA2 de la variable dont on a le nom préfixé de @
        pour un mot de taille wordSize bits

        :param name: nom de la variable
        :type name: str
        :param wordSize: taille du mot binaire
        :type wordSize: int
        :return: code CA2 de la valeur initiale de la variable, sur wordSize bits
        :rtype: str
        :raises: CompilationError

        :Example:
            >>> Variable.binary("@x", 8)
            '00000000'

            >>> Variable.binary("@#m45", 8)
            '11010011'

            >>> Variable("@#1000",8).getValueBinary(8)
            Traceback (most recent call last):
            ...
            CompilationError: @#1000 : Variable de valeur trop grande !
        """
        value = Variable.toInt(name)
        if value < 0:
            # utilise le CA2
            valueToCode = (~(-value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize or value > 0 and outStr[0] == '1':
            raise CompilationError("{} : Variable de valeur trop grande !".format(name))
        return outStr

    @staticmethod
    def asm(name:str) -> str:
        """Retourne chaîne de caractère représentant le code asm de la variable dont on a le nom préfixé de @

        :param name: nom de la variable
        :type name: str
        :return: code ASM
        :rtype: str

        :Example:
            >>> Variable.asm("@x")
            '@x\t0'

            >>> Variable.asm("@#m45")
            '@#m45\t45'
        """
        value = Variable.toInt(name)
        return "{}\t{}".format(name, value)

    @classmethod
    def fromInt(cls, value:int) -> 'Variable':
        """
        Crée une variable destinée à contenir un littéral
        :param value: valeur du littéral
        :type value: int
        :return: objet variable créé
        :rtype: Variable
        """
        if value < 0:
            name = "#m{}".format(abs(value))
        else:
            name = "#{}".format(value)
        v = Variable(name)
        v._value = value
        return v

    @property
    def name(self) -> str:
        """Retourne le nom de la variable

        :return: nom de la variable
        :rtype: str

        :Example:
            >>> Variable("x").name
            'x'

        .. warning:: Il est possible que l'on crée plusieurs variables pour un même nom
        """

        return self._name

    def __str__(self) -> 'str':
        """Transtypage -> str. Affiche le nom de la variable préfixé par @

        :return: @ + nom de la variable
        :rtype: str

        :Example:
            >>> str(Variable("x"))
            '@x'

        """

        return "@{}".format(self._name)

    @property
    def value(self) -> int:
        """Retourne la valeur initiale de la variable

        :return: valeur initiale de la variable
        :rtype: int

        :Example:
            >>> Variable("x").value
            0

            >>> Variable.fromInt(15).value
            15
        """
        return Variable.toInt(self._name)
    