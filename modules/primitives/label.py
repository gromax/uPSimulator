"""
.. module:: label
   :synopsis: définition d'un objet contenant une étiquette
"""

class Label:
    PREFIX = "Lab"
    _currentIndex = 0 # type: int
    _name:str = ''

    @classmethod
    def getNextFreeIndex(cls) -> int:
        """génère un nouvel index de numéro de label. Assure l'unicité des numéros.

        :return: index pour un nouveau label
        :rtype: int
        """
        cls._currentIndex += 1
        return cls._currentIndex

    def __init__(self):
        """Constructeur de la classe
        """
        pass

    @property
    def name(self) -> 'str':
        """Assigne le nom si nécessaire et le retourne

        :return: nom de l'étiquette
        :rtype: str
        """

        if self._name == "":
            index = Label.getNextFreeIndex()
            self._name = self.PREFIX+str(index)
        return self._name

    def __str__(self) -> 'str':
        """Transtypage -> str. Affiche le nom de l'étiquette

        :return: nom de l'étiquette
        :rtype: str

        :Example:
            >>> str(Label())
            'Lab1'

        """
        return self.name

