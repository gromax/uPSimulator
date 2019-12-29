from errors import *

DEFAULT_ENGINE_ATTRIBUTES = {
  "memory_address_bits": 9,
  "litteral_bits": 6,
  "register_address_bits":3,
  "free_ual_output": True,
  "data_bits": 16,
  "halt":   { "opcode":"00000", "asm":"HALT" },
  "goto":   { "opcode":"00001", "asm":"JMP" },
  "!=":    { "opcode":"0001000", "asm":"BNE" },
  "==":    { "opcode":"0001001", "asm":"BEQ" },
  "<":    { "opcode":"0001010", "asm":"BLT" },
  ">":    { "opcode":"0001011", "asm":"BGT" },
  "cmp":    { "opcode":"00011", "asm":"CMP" },
  "print":  { "opcode":"00100", "asm":"PRINT" },
  "input":  { "opcode":"00101", "asm":"INPUT" },
  "load":   { "opcode":"0011", "asm":"LOAD" },
  "move":   { "opcode":"01000", "asm":"MOVE" },
  "move_l": { "opcode":"01001", "asm":"MOVE" },
  "neg":    { "opcode":"010100", "asm":"NEG"},
  "~":      { "opcode":"010101", "asm":"NOT"},
  "neg_l":  { "opcode":"010110", "asm":"NEG"},
  "~_l":    { "opcode":"010111", "asm":"NOT"},
  "+":      { "opcode":"0110000", "asm":"ADD"},
  "-":      { "opcode":"0110001", "asm":"SUB"},
  "*":      { "opcode":"0110010", "asm":"MULT"},
  "/":      { "opcode":"0110011", "asm":"DIV"},
  "%":      { "opcode":"0110100", "asm":"MOD"},
  "&":      { "opcode":"0110101", "asm":"AND"},
  "|":      { "opcode":"0110110", "asm":"OR"},
  "^":      { "opcode":"0110111", "asm":"XOR"},
  "store":  { "opcode":"0111", "asm":"STORE"},
  "+_l":    { "opcode":"1000", "asm":"ADD"},
  "-_l":    { "opcode":"1001", "asm":"SUB"},
  "*_l":    { "opcode":"1010", "asm":"MULT"},
  "/_l":    { "opcode":"1011", "asm":"DIV"},
  "%_l":    { "opcode":"1100", "asm":"MOD"},
  "&_l":    { "opcode":"1101", "asm":"AND"},
  "|_l":    { "opcode":"1110", "asm":"OR"},
  "^_l":    { "opcode":"1111", "asm":"XOR"}
}


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
      if not "memory_address_bits" in self.__attributes or not isinstance(self.__attributes["memory_address_bits"],int) or self.__attributes["memory_address_bits"] < 1:
        raise AttributeError("Attribut 'memory_adress_bits' manquant ou incorrect")
      if "litteral_bits" in self.__attributes and ( not isinstance(self.__attributes["litteral_bits"],int) or self.__attributes["litteral_bits"] < 1):
        raise AttributeError("Attribut 'litteral_bits' incorrect")
      if not "register_address_bits" in self.__attributes or not isinstance(self.__attributes["register_address_bits"],int) or self.__attributes["register_address_bits"] < 1:
        raise AttributeError("Attribut 'register_address_bits' manquant ou incorrect")
      if not "data_bits" in self.__attributes or not isinstance(self.__attributes["data_bits"],int) or self.__attributes["data_bits"] < 1:
        raise AttributeError("Attribut 'data_bits' manquant ou incorrect")
      return True

    def registersNumber(self):
        return 2**self.__attributes["register_address_bits"]

    def litteralInCommand(self):
        return "litteral_bits" in self.__attributes

    def maxLitteral(self):
        if not self.litteralInCommand():
          return 0
        return 2**self.__attributes["litteral_bits"] - 1

    def ualOutputIsFree(self):
        return self.__freeUalOutput

    def hasNEG(self):
        return "neg" in self.__attributes

    def litteralOperatorAvailable(self, operator):
        return self.litteralInCommand() and operator+"_l" in self.__attributes

    def hasOperator(self, operator):
        return operator in self.__attributes

    def getASM(self, **kwargs):
        assert "operator" in kwargs
        operator = kwargs["operator"]
        assert operator in self.__attributes
        strAsm = self.__attributes[operator]["asm"]+" "

        if "ualCible" in kwargs:
            ualCible = kwargs["ualCible"]
            assert ualCible == 0 or self.ualOutputIsFree()
            if self.ualOutputIsFree():
                strAsm += "r"+str(ualCible)+", "
        if "operands" in kwargs:
            operands = kwargs["operands"]
            strOps = []
            for op in operands:
                if isinstance(op, int):
                    strOps.append("r"+str(op))
                else:
                    strOps.append(str(op))
            strAsm += ", ".join(strOps)
        elif "operand" in kwargs:
            op = kwargs["operand"]
            if isinstance(op, int):
                strOp = "r"+str(op)
            else:
                strOp = str(op)
            strAsm += strOp
        return strAsm

    def lookForComparaison(self, comparaisonSymbol):
        '''
        indique quelle opération à effectuer pour obtenir un symbole de comparaison disponible
        dans a < b on peut transformer en :
        -  b > a, ce qui ne change rien au fonctionnement (miroir) -> à privilégier
        -  not(a>=b), ce qui intervertit les branchements (négation)
        Sortie = mirroir, négation
        '''
        if comparaisonSymbol in self.__attributes:
            return (False, False)
        negation = { "<":">=", ">":"<=", "<=":">", ">=":"<", "==":"!=", "!=":"==" }
        miroir = { "<":">", ">":"<", "<=":"=>", ">=":"<=" }
        if comparaisonSymbol in miroir and miroir[comparaisonSymbol] in self.__attributes:
            return (True, False)
        if comparaisonSymbol in negation and negation[comparaisonSymbol] in self.__attributes:
            return (False, True)
        if comparaisonSymbol in miroir:
            miroirSymbol == miroir[comparaisonSymbol]
            if miroirSymbol in negation and negation[miroirSymbol] in self.__attributes:
                return (True,True)
        return None


if __name__=="__main__":
    engine = ProcessorEngine()
