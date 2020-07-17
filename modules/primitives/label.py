"""
.. module:: label
   :synopsis: définition d'un objet contenant une étiquette
"""

class Label:
    PREFIX = "Lab"
    _currentIndex = 0 # type: int
    _name:str = ''
    _index:int = -1

    @classmethod
    def getNextFreeIndex(cls) -> int:
        """génère un nouvel index de numéro de label. Assure l'unicité des numéros.

        :return: index pour un nouveau label
        :rtype: int
        """
        cls._currentIndex += 1
        return cls._currentIndex

    @classmethod
    def initFreeIndex(cls):
        """
        remet à 0 le _currentIndex
        utile en cas de compilation de plusieurs programmes à la suite
        """
        cls._currentIndex = 0

    def __init__(self):
        """Constructeur de la classe
        """
        pass

    def initIndex(self):
        """
        remet à 0 le _currentIndex
        utile en cas de compilation de plusieurs programmes à la suite
        """
        self._index = Label.getNextFreeIndex()
    
    @property
    def name(self) -> 'str':
        """Assigne le nom si nécessaire et le retourne

        :return: nom de l'étiquette
        :rtype: str
        """
        if self._index == -1:
            self._index = Label.getNextFreeIndex()
        return self.PREFIX+str(self._index)

    def __str__(self) -> 'str':
        """Transtypage -> str. Affiche le nom de l'étiquette

        :return: nom de l'étiquette
        :rtype: str

        :Example:
            >>> str(Label())
            'Lab1'

        """
        return self.name

