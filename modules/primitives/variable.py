"""
.. module:: variable
   :synopsis: définition d'un objet contenant une variable mémoire
"""

from modules.errors import CompilationError

class Variable:
    def __init__(self, nom:str, value:int = 0):
        """Constructeur de la classe

        :param nom: nom de la variable
        :type nom: str
        :param value: valeur initiale. 0 par défaut
        :type value: int
        """
        self._name = nom
        self._value = value

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

        return "@"+self._name

    def getValueBinary(self, wordSize:int) -> 'str':
        """Retourne chaîne de caractère représentant le code CA2 de self._value,
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

        if self._value < 0:
            # utilise le CA2
            valueToCode = (~(-self._value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self._value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize or self._value > 0 and outStr[0] == '1':
            raise CompilationError(f"{self} : Variable de valeur trop grande !")
        return outStr

    @property
    def value(self) -> int:
        """Retourne la valeur initiale de la variable

        :return: valeur initiale de la variable
        :rtype: int

        :Example:
            >>> Variable("x").value
            0

            >>> Variable("x",15).value
            15

        """
        return self._value
