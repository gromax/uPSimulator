from errors import *
from variablemanager import Litteral, Variable

DEFAULT_ENGINE_ATTRIBUTES = {
  "memory_address_bits": 9,
  "litteral_bits": 6,
  "register_address_bits":3,
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

    def getRegisterCode(self,registerIndex):
        assert 0 <= registerIndex < self.registersNumber()
        nbits = self.__attributes["register_address_bits"]
        return format(registerIndex,'0'+str(nbits)+'b')

    def getLitteralCode(self, litteralValue):
        assert 0 <= litteralValue
        if litteralValue > self.maxLitteral():
            litteralValue = self.maxLitteral()
        nbits = self.__attributes["litteral_bits"]
        return format(litteralValue,'0'+str(nbits)+'b')

    def getFullLitteralCode(self, litteralValue):
        nbits = self.__attributes["data_bits"]
        if not -2**(nbits-1)<= litteralValue < 2**(nbits-1):
            raise CompilationError(f"Litteral {litteralValue} trop grand.")
        if litteralValue >= 0:
            return format(litteralValue,'0'+str(nbits)+'b')
        # calcul utilisant le ca2
        ca2 = (~ abs(litteralValue)) & (2**nbits-1) + 1
        return format(ca2,'0'+str(nbits)+'b')

    def getAddressCode(self, addressValue):
        assert 0 <= addressValue
        nbits = self.__attributes["memory_address_bits"]
        if addressValue >= 2**nbits:
            raise CompilationError(f"Addresse {addressValue} trop grande.")
        return format(addressValue,'0'+str(nbits)+'b')

    def ualOutputIsFree(self):
        return self.__freeUalOutput

    def hasNEG(self):
        return "neg" in self.__attributes

    def litteralOperatorAvailable(self, operator):
        return self.litteralInCommand() and operator+"_l" in self.__attributes

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

    def getAsmDesc(self, attributes):
        '''
        attributes = Dictionnaire contenant des élément optionnels :
        - lineNumber
        - operator (obligatoire)
        - litteral
        - operands
        - ualCible
        '''
        if "lineNumber" in attributes:
            lineNumber = attributes["lineNumber"]
        else:
            lineNumber = 0
        assert "operator" in attributes
        operator = attributes["operator"]
        if "litteral" in attributes and attributes["litteral"] == True:
            operator += "_l"
            islitteralOp = True
        else:
            islitteralOp = False
        assert operator in self.__attributes
        strAsmCommand = self.__attributes[operator]["asm"]
        opcode = self.__attributes[operator]["opcode"]
        opNumber = self.__attributes[operator]["opnumber"]
        if "operands" in attributes:
            operands = attributes["operands"]
        else:
            operands = tuple()
        if "ualCible" in attributes:
            ualCible = attributes["ualCible"]
            assert ualCible == 0 or self.ualOutputIsFree()
            if self.ualOutputIsFree():
                operands = (ualCible,) + operands
        assert len(operands) == opNumber
        assert islitteralOp == False or len(operands) > 0 and isinstance(operands[-1],Litteral)
        outDesc = { "command":strAsmCommand, "opcode":opcode, "operands":operands, "lineNumber":lineNumber }
        if islitteralOp:
            litt = operands[-1]
            value = litt.getValue()
            if value > self.maxLitteral():
                outDesc["litteralNextLine"] = litt
        return outDesc

    def getBinary(self, asmDesc, vm, baseMemoryIndex, labelIndexList):
        '''
        asmDesc = description assembleur
        vm = VariableManager
        memoryIndex = index mémoire pour la première mémoire
        retourne le code binaire
        labelIndexList = dict clé = label, value = index
        '''
        if "litteral" in asmDesc:
            # simple litteral
            litt = asmDesc["litteral"]
            litteralValue = litt.getValue()
            return self.getFullLitteralCode(litteralValue)
        if not "opcode" in asmDesc:
            return self.getFullLitteralCode(0)
        opcode = asmDesc["opcode"]
        if not "operands" in asmDesc:
            operandsBinaryStr = ""
        else:
            operands = asmDesc["operands"]
            operandsBinaryList = []
            for index, op in enumerate(operands):
                if isinstance(op,int):
                    # c'est un registre
                    self.__attributes["register_address_bits"]
                    code = self.getRegisterCode(op)
                    operandsBinaryList.append(code)
                elif isinstance(op,Litteral):
                    assert index == len(operands)-1
                    value = op.getValue()
                    code = self.getLitteralCode(value)
                    operandsBinaryList.append(code)
                elif isinstance(op,Variable):
                    assert index == len(operands)-1
                    address = vm.getMemoryIndex(op, baseMemoryIndex)
                    code = self.getAddressCode(address)
                    operandsBinaryList.append(code)
                elif isinstance(op,str):
                     # il s'agit d'une étiquette
                     assert op in labelIndexList
                     address = labelIndexList[op]
                     code = self.getAddressCode(address)
                     operandsBinaryList.append(code)
                else:
                    raise CompilationError("Opérande invalide")
            operandsBinaryStr = "".join(operandsBinaryList)
        missingDigits = self.__attributes["data_bits"] - len(opcode) - len(operandsBinaryStr)
        assert missingDigits >= 0
        return opcode + "0"*missingDigits + operandsBinaryStr

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
