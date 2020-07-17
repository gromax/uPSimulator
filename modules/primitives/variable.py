"""
.. module:: variable
   :synopsis: définition d'un objet contenant une variable mémoire
"""

from typing import Dict, Optional
from modules.errors import CompilationError

class Variable:
    _value:int = 0
    _variableManager:Optional['VariableManager'] = None

    @classmethod
    def getVariableManager(cls) -> 'VariableManager':
        if cls._variableManager is None:
            cls._variableManager = VariableManager()
        return cls._variableManager
    
    @classmethod
    def resetVariableManager(cls) -> 'VariableManager':
        cls._variableManager = None
        return cls.getVariableManager()
    
    @classmethod
    def add(cls, name) -> 'Variable':
        return cls.getVariableManager().add(name)

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
        v = Variable.add(name)
        v._value = value
        return v

    def __init__(self, nom:str):
        """Constructeur de la classe

        :param nom: nom de la variable
        :type nom: str
        """
        self._name = nom

    def _isLitteral(self) -> bool:
        """Prédicat
        :return: cette variable contient un littéral de valeur fixe
        :rtype: bool
        """
        return self._name[0] == "#"

    def setInitialValue(self, value:int):
        """Affecte une valeur initiale
        
        :param: valeur initiale
        :type: int
        """
        assert not self._isLitteral()
        self._value = value

    def binary(self, wordSize:int) -> 'str':
        """Retourne chaîne de caractère représentant le code CA2 de la variable
        pour un mot de taille wordSize bits

        :param wordSize: taille du mot binaire
        :type wordSize: int
        :return: code CA2 de la valeur initiale de la variable, sur wordSize bits
        :rtype: str
        :raises: CompilationError

        :Example:
            >>> Variable("x").binary(8)
            '00000000'

            >>> Variable.fromInt(45).binary(8)
            '11010011'

            >>> Variable.fromInt(1000,8)
            Traceback (most recent call last):
            ...
            CompilationError: @#1000 : Variable de valeur trop grande !
        """
        if self._value < 0:
            # utilise le CA2
            valueToCode = (~(- self._value) + 1) & (2**wordSize - 1)
        else:
            valueToCode = self._value
        outStr = format(valueToCode, '0'+str(wordSize)+'b')
        if len(outStr) > wordSize or self._value > 0 and outStr[0] == '1':
            raise CompilationError("{} : Variable de valeur trop grande !".format(self))
        return outStr

    def asm(self) -> str:
        """Retourne chaîne de caractère représentant le code asm de la variable

        :return: code ASM
        :rtype: str

        :Example:
            >>> Variable("x").asm()
            '@x\t0'

            >>> Variable.fromInt(45).asm()
            '@#m45\t45'
        """
        return "{}\t{}".format(self, self._value)

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
        return self._value


class VariableManager:
    _list:Dict[str,Variable]
    def __init__(self):
        self._list = {}
    
    def add(self, name:str) -> Variable:
        """Ajoute si nécessaire la variable correspondante

        :param nom: nom de la variable
        :type nom: str
        """
        if not name in self._list:
            self._list[name] = Variable(name)
        return self._list[name]

