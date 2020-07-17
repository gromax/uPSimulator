"""
.. module:: processorengine
   :synopsis: classe définissant les attributs d'un modèle de processeur et fournissant les informations utiles aux outils de compilation
"""

from typing import Union, List, Dict, Optional, Tuple, Sequence, Any
from abc import ABC, ABCMeta, abstractmethod

from modules.errors import CompilationError
from modules.primitives.litteral import Litteral
from modules.primitives.variable import Variable
from modules.primitives.register import Register
from modules.primitives.label import Label
from modules.primitives.operators import Operator, Operators
from modules.primitives.actionsfifo import ActionsFIFO, ActionType
from modules.engine.asmgenerator import AsmGenerator
from modules.engine.decode import Decodeur, Decoded, DefaultDecoded

class ProcessorEngine(metaclass=ABCMeta):
    _name                  :str
    _register_address_bits :int
    _data_bits             :int
    _freeUalOutput         :bool
    
    _asmGenerators       : Tuple[AsmGenerator,...]
    _decodeurs           : Tuple[Decodeur,...]
    _comparaisonOperators: List[Operator]
    _litteralDomain      :Tuple[int, int]

    def __init__(self):
        """Constructeur

        :param name: nom du modèle de processeur utilisé
        :type name: str
        """
        if self.ualOutputIsFree():
            destReg = 1
        else:
            destReg = 0
        self.__opNumber = {
            "neg":  1 + destReg,
            "move": 2,
            "+":    2 + destReg,
            "-":    2 + destReg,
            "*":    2 + destReg,
            "/":    2 + destReg,
            "%":    2 + destReg,
            "&":    2 + destReg,
            "|":    2 + destReg,
            "^":    2 + destReg,
            "~":    1 + destReg,
        }

    @property
    def name(self):
        return self._name

    def registersNumber(self) -> int:
        """Calcul le nombre de registres considérant l'adressage disponible

        :return: nombre de registre
        :rtype: int
        """
        return 2**self._register_address_bits

    def ualOutputIsFree(self) -> bool:
        """Accesseur

        :return: Vrai si on peut choisir le registre de sortie de l'UAL
        :rtype: bool
        """
        return self._freeUalOutput
    '''
    def getOpcode(self, operator:Operator) -> str:
        """Renvoie l'opcode de la commande demandée. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: opcode sous forme binaire
        :rtype: str
        """

        if not operator in self._commands:
            return ""
        itemAttribute = self._commands[operator]
        return itemAttribute["opcode"]


    def getLitteralOpcode(self, operator:Operator) -> str:
        """Renvoie l'opcode de la commande demandée dans sa version acceptant un littéral. ``''`` si introuvable.

        :param operator: nom de la commande
        :type operator: Operator
        :return: opcode sous forme binaire
        :rtype: str
        """

        if not operator in self._litteralsCommands:
            return ""
        itemAttribute = self._litteralsCommands[operator]
        return itemAttribute["opcode"]
    '''

    def litteralOperatorAvailable(self, operator:Operator, litteral:Litteral) -> bool:
        """Teste si la commande peut s'éxécuter dans une version acceptant un littéral, avec ce littéral en particulier. Il faut que la commande accepte les littéraux et que le codage de ce littéral soit possible dans l'espace laissé par cette commande.

        :param operator: commande à utiliser
        :type operator: Operator
        :param litteral: littéral à utiliser
        :type litteral: Litteral
        :return: vrai si la commande est utilisable avec ce littéral
        :rtype: bool
        """
        # pas de littéral par défaut
        return False

    def instructionDecode(self, binary:Union[int,str]) -> Decoded:
        """Pour une instruction, fait le décodage en renvoyant le descriptif commande, les opérandes registres et un éventuel opérande non registre

        :param binary: code binaire
        :type binary: int ou str
        :result: objet contenant l'opérateur et les arguments
        :rtype: Decoded

        """
        if isinstance(binary, int):
            strBinary = format(binary, '0'+str(self._data_bits)+'b')
        else:
            strBinary = binary
        
        for decodeurItem in self._decodeurs:
            if decodeurItem.match(strBinary):
                return decodeurItem.decode(strBinary)
        # aucune instruction trouvée
        return DefaultDecoded
 
    @property
    def litteralDomain(self) -> Tuple[int, int]:
        return self._litteralDomain

    def valueFitsInMemory(self, value:int, posValue:bool) -> bool:
        """Teste si une valeur a une valeur qui pourra être codée en mémoire

        :param value: valeur à tester
        :type value: int
        :param posValue: la valeur doit être codée en nombre positif
        :type posValue: bool
        :return: la valeur peut être codée en mémoire
        :rtype: bool
        """
        nb = self._data_bits
        if posValue:
            # peut aller de 0 à 2^nb - 1
            return 0 <= value < 2**nb
        # peut aller de -2^(nb-1) à 2^(nb-1)-1
        if value >=0:
            return value < 2**(nb - 1)
        return value >= 2**(nb - 1)

    def getComparaisonSymbolsAvailables(self) -> List[Operator]:
        """Accesseur

        :return: liste des symboles de comparaison disponibles avec ce modèle de processeur
        :rtype: list[Operator]
        """

        return [item for item in self._comparaisonOperators if item.isComparaison]

    @property
    def regBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage de l'adresse d'un registre
        :rtype: int
        """
        return self._register_address_bits

    @property
    def dataBits(self) -> int:
        """Accesseur

        :return: nombre de bits utilisés pour l'encodage d'une donnée en mémoire
        :rtype: int
        """
        return self._data_bits
    
    # fonctions -> ASM
    def _operatorToAsm(self, operator:Operator, operands:List[ActionType]) -> List[str]:
        """
        :param operator: Opérateur en cours
        :type operator: Operator 
        :param operands: opérandes de l'opération en cours
        :type operands: List[ActionType]
        :return: code asm
        :rtype: List[str]
        :raise: CompilationError
        """
        for asmGen in self._asmGenerators:
            if asmGen.operator != operator or not asmGen.sastifyConditions(operands):
                continue
            return asmGen.asm(operands)
        strOperands = ", ".join([str(it) for it in operands])
        raise CompilationError("Aucun opérateur asm disponible pour la séquence : {} -> [{}]".format(strOperands, operator))

    def _actionToAsm(self, fifo:ActionsFIFO) -> List[str]:
        """
        :param fifo: file des actions produite par la compilation
        :type fifo: ActionsFIFO
        :return: code asm
        :rtyp: List[str]
        :raises: CompilationError
        """

        lines: List[str] = []
        currentActionItems:List[ActionType] = []
        while not fifo.empty:
            lastItem = fifo.pop()
            if (not isinstance(lastItem, Operator)) or lastItem.isComparaison:
                currentActionItems.append(lastItem)
                continue
            lines.extend(self._operatorToAsm(lastItem, currentActionItems))
            currentActionItems = []

        if len(currentActionItems) > 0:
            raise CompilationError("La séquence devrait terminer par un opérateur.", {"lineNumber":fifo.lineNumber})

        return lines

    def _getVariablesList(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]]) -> List[Variable]:
        """
        :param fifos: file d'actions
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :return: liste des noms de variables
        :rtype: List[str]
        """
        if isinstance(fifos, ActionsFIFO):
            return fifos.getVariablesList()
        variablesList:List[Variable] = []
        for fifo in fifos:
            variablesList = fifo.getVariablesList(variablesList)
        return variablesList

    def _getLabelsList(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]]) -> List[Label]:
        """
        :param fifos: file d'actions
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :return: liste des labels
        :rtype: List[Label]
        """
        if not isinstance(fifos, list):
            fifos = [fifos]
        return [fifo.label for fifo in fifos if not fifo.label is None]

    def _getVariablesBinary(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]]) -> List[str]:
        """
        :param fifos: file d'actions
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :return: liste des noms de variables
        :rtype: List[str]
        """
        variablesList = self._getVariablesList(fifos)
        return [v.binary(self.dataBits) for v in variablesList]

    def getAsm(self, fifos:Union[ActionsFIFO, List[ActionsFIFO]], withVariables:bool=False) -> str:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: Union[ActionsFIFO, List[ActionsFIFO]]
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: code asm
        :rtype: str
        :raises: CompilationError
        """
        if isinstance(fifos, ActionsFIFO):
            fifoAsmlines = self._actionToAsm(fifos.clone())
            outAsm = "\n".join(fifos.prependStrLabel(fifoAsmlines))
        else:
            listFifoAsmLines = ["\n".join(fifo.prependStrLabel(self._actionToAsm(fifo.clone()))) for fifo in fifos]
            outAsm = "\n".join(listFifoAsmLines)
        if not withVariables:
            return outAsm
        variablesAsm = "\n".join([v.asm() for v in self._getVariablesList(fifos)])
        return "\n".join([outAsm, variablesAsm])
        
    # Fonction -> code
    def _getAdresses(self, fifos:List[ActionsFIFO]) -> Dict[Union[Label,Variable],int]:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: ActionsFIFO
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: liste des labels et variables avec numéro de ligne dans le code
        :rtyp: Dict[Union[Label,Variable],int]
        """
        # il faut identifier les numéros de ligne qui accueilleront les variables et les labels
        variablesListWithoutLine = self._getVariablesList(fifos)
        addressList:Dict[Union[Label,Variable],int] = {}
        lineCount = 0
        for act in fifos:
            if not act.label is None:
                addressList[act.label] = lineCount
            asmLines = self._actionToAsm(act.clone())
            lineCount += len(asmLines)
        for v in variablesListWithoutLine:
            addressList[v] = lineCount
            lineCount += 1
        return addressList

    def _operatorToBinary(self, operator:Operator, operands:List[ActionType], addressList:Dict[Union[Label, Variable],int]) -> List[str]:
        """
        :param operator: Opérateur en cours
        :type operator: Operator 
        :param operands: opérandes de l'opération en cours
        :type operands: List[ActionType]
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label, Variable],int]
        :return: code binaire
        :rtype: List[str]
        :raise: CompilationError
        """
        for asmGen in self._asmGenerators:
            if asmGen.operator != operator or not asmGen.sastifyConditions(operands):
                continue
            return asmGen.binary(operands,addressList)
        strOperands = ", ".join([str(it) for it in operands])
        raise CompilationError("Aucun opérateur asm disponible pour la séquence : {} -> [{}]".format(strOperands, operator))

    def _actionToBinary(self, fifo:ActionsFIFO, addressList:Dict[Union[Label,Variable],int]) -> List[str]:
        """
        :param fifo: file des actions produite par la compilation
        :type fifo: ActionsFIFO
        :param addressList: adresses de variables et labels
        :type addressList: Dict[Union[Label,Variable],int]
        :return: code binaire
        :rtyp: List[str]
        """

        lines: List[str] = []
        currentActionItems:List[ActionType] = []
        while not fifo.empty:
            lastItem = fifo.pop()
            if (not isinstance(lastItem, Operator)) or lastItem.isComparaison:
                currentActionItems.append(lastItem)
                continue
            lines.extend(self._operatorToBinary(lastItem, currentActionItems, addressList))
            currentActionItems = []

        if len(currentActionItems) > 0:
            raise CompilationError("La séquence devrait terminer par un opérateur.", {"lineNumber":fifo.lineNumber})

        return lines


    def getBinary(self, fifos:List[ActionsFIFO]) -> List[str]:
        """
        :param fifos: file des actions produite par la compilation
        :type fifos: List[ActionsFIFO]
        :param withVariables: Faut-il joindre les variables au code asm
        :type withVariables: bool
        :return: code binaire
        :rtype: List[str]
        """
        addressList = self._getAdresses(fifos)
        outCode = []
        variablesCode = self._getVariablesBinary(fifos) 
        for fifo in fifos:
            outCode.extend(self._actionToBinary(fifo.clone(), addressList))
        outCode.extend(variablesCode)
        return outCode
            

