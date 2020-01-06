from errors import *

DEFAULT_ENGINE_ATTRIBUTES = {
  "register_bits":3,
  "free_ual_output": True,
  "data_bits": 16,
  "halt":   { "opcode":"00000", "asm":"HALT", "opnumber":0 },
  "goto":   { "opcode":"00001", "asm":"JMP", "opnumber":1 },
  "!=":    { "opcode":"0001000", "asm":"BNE", "opnumber":1 },
  "==":    { "opcode":"0001001", "asm":"BEQ", "opnumber":1 },
  "<":    { "opcode":"0001010", "asm":"BLT", "opnumber":1 },
  ">":    { "opcode":"0001011", "asm":"BGT", "opnumber":1 },
  "cmp":    { "opcode":"00011", "asm":"CMP", "opnumber":2 },
  "print":  { "opcode":"00100", "asm":"PRINT", "opnumber":1 },
  "input":  { "opcode":"00101", "asm":"INPUT", "opnumber":1 },
  "load":   { "opcode":"0011", "asm":"LOAD", "opnumber":2 },
  "move":   { "opcode":"01000", "asm":"MOVE", "opnumber":2 },
  "move_l": { "opcode":"01001", "asm":"MOVE", "opnumber":2 },
  "neg":    { "opcode":"010100", "asm":"NEG", "opnumber":2},
  "~":      { "opcode":"010101", "asm":"NOT", "opnumber":2},
  "neg_l":  { "opcode":"010110", "asm":"NEG", "opnumber":2},
  "~_l":    { "opcode":"010111", "asm":"NOT", "opnumber":2},
  "+":      { "opcode":"0110000", "asm":"ADD", "opnumber":3},
  "-":      { "opcode":"0110001", "asm":"SUB", "opnumber":3},
  "*":      { "opcode":"0110010", "asm":"MULT", "opnumber":3},
  "/":      { "opcode":"0110011", "asm":"DIV", "opnumber":3},
  "%":      { "opcode":"0110100", "asm":"MOD", "opnumber":3},
  "&":      { "opcode":"0110101", "asm":"AND", "opnumber":3},
  "|":      { "opcode":"0110110", "asm":"OR", "opnumber":3},
  "^":      { "opcode":"0110111", "asm":"XOR", "opnumber":3},
  "store":  { "opcode":"0111", "asm":"STORE", "opnumber":2},
  "+_l":    { "opcode":"1000", "asm":"ADD", "opnumber":3},
  "-_l":    { "opcode":"1001", "asm":"SUB", "opnumber":3},
  "*_l":    { "opcode":"1010", "asm":"MULT", "opnumber":3},
  "/_l":    { "opcode":"1011", "asm":"DIV", "opnumber":3},
  "%_l":    { "opcode":"1100", "asm":"MOD", "opnumber":3},
  "&_l":    { "opcode":"1101", "asm":"AND", "opnumber":3},
  "|_l":    { "opcode":"1110", "asm":"OR", "opnumber":3},
  "^_l":    { "opcode":"1111", "asm":"XOR", "opnumber":3}
}

class Register:
    def __init__(self, index, isUalOnlyOutput):
        self.__index = index
        self.isUalOnlyOutput = __isUalOnlyOutput == True

    def __str__(self):
        return "r"+str(self.__index)

class ProcessorEngine:
    def __init__(self, **options):
      '''
      pour l'instant, les paramètres sont forcément définis par le DEFAULT_ENGINE_ATTRIBUTES
      à venir : possibilité de charger un objet ou un fichier
      '''
      self.__attributes = DEFAULT_ENGINE_ATTRIBUTES
      assert self.__checkAttributes() == True
      self.__freeUalOutput = "free_ual_output" in self.__attributes and (self.__attributes["free_ual_output"] == True or self.__attributes["free_ual_output"] == 1)

    def __checkAttributes(self):
      if not "register_bits" in self.__attributes or not isinstance(self.__attributes["register_bits"],int) or self.__attributes["register_bits"] < 1:
        raise AttributeError("Attribut 'register_bits' manquant ou incorrect")
      if not "data_bits" in self.__attributes or not isinstance(self.__attributes["data_bits"],int) or self.__attributes["data_bits"] < 1:
        raise AttributeError("Attribut 'data_bits' manquant ou incorrect")
      return True

    def registersNumber(self):
        return 2**self.__attributes["register_bits"]

    def ualOutputIsFree(self):
        return self.__freeUalOutput

    def hasNEG(self):
        return "neg" in self.__attributes

    def hasOperator(self, operator):
        return operator in self.__attributes

    def getRegisterList(self):
        '''
        génère une liste de registre disponibles à usage d'un manager de compilation
        '''
        if self.__freeUalOutput:
            r0 = Register(0,False)
        else:
            r0 = Register(0,True)
        regs = [r0]
        for i in range(1,self.registersNumber()):
            regs.append(Register(i,False))
        return regs.reverse()

    def getAsmCommand(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour asm, None si n'existe pas
        '''
        if not commandDesc in self.__attributes:
            return None
        itemAttribute = self.__attributes[commandDesc]
        return itemAttribute["asm"]

    def getOpcode(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        sortie = string pour opcode, None si n'existe pas
        '''
        if not commandDesc in self.__attributes:
            return None
        itemAttribute = self.__attributes[commandDesc]
        return itemAttribute["opcode"]

    def litteralOperatorAvailable(self, operator, litteral):
        '''
        operator = nom d'une opération arithmétique ou logique
        litteral = objet Litteral
        Retourne True si l'opérateur existe en version littéral
        et qu'il est possible de l'utiliser avec ce littéral.
        Le cas où ce ne serait pas possible serait celui où le littéral
        serait trop grand et que l'on ne prévoirait pas de le placer à la ligne suivante.
        '''
        operatorForLitteral = operator + "_l"
        if not operatorForLitteral in self.__attributes:
            return False
        if self.bigLitteralIsNextLine():
            return True
        maxLitteralSize = self.getLitteralMaxSizeIn(operatorForLitteral)
        return maxLitteralSize >= litteral.getValue()

    def bigLitteralIsNextLine(self):
        if "bigLitteralIsNextLine" in self.__attributes:
            return self.__attributes["bigLitteralIsNextLine"] == True
        return False

    def getLitteralMaxSizeIn(self, commandDesc):
        '''
        commandDesc = chaîne de caractère décrivant un type de commande
        retourne la taille du litteral maximum dans une commande
        '''
        assert commandDesc in self.__attributes
        commandAttributes = self.__attributes[commandDesc]
        # on suppose toujours que le littéral peut occuper toute la place restante
        # il faut calculer la place disponible
        nbits_total = self.__attributes["data_bits"]
        nbits_reg = self.__attributes["register_bits"]
        nb_reg_operands = self.__attributes[commandDesc]["opnumber"] - 1
        opcode = self.__attributes[commandDesc]["opcode"]
        nbits = nbits_total - nb_reg_operands * nbits_reg - len(opcode)
        if nbits <=0:
            raise AttributeError(f"Pas assez de place pour un littéral dans {commandDesc}.")
        return 2**nbits - 2

    def getComparaisonSymbolsAvailables(self):
        '''
        Retourne la liste des symbole de comparaison disponibles dans le modèle
        '''
        symbols = ["<=", "<", ">=", ">", "==", "!="]
        return [item for item in symbols if item in self.__attributes]

    def getRegBits(self):
        return self.__attributes["register_bits"]

    def getDataBits(self):
        return self.__attributes["data_bits"]


if __name__=="__main__":
    engine = ProcessorEngine()
