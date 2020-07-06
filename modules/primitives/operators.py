"""
.. module:: operators
:synopsis: définit les symboles liés au différents opérateurs et leurs propriétés
"""

from typing import List

class Operator:
  ARITHMETIC  = 1
  LOGIC       = 2
  COMPARAISON = 3
  COMMAND     = 4
  OTHER       = 0
  _arity        :int
  _isCommutatif :bool
  _regex        :str
  _symbol       :str
  _type         :int
  _priority     :int

  @property
  def isArithmetic(self) -> bool:
    return self._type == Operator.ARITHMETIC

  @property
  def isComparaison(self) -> bool:
    return self._type == Operator.COMPARAISON

  @property
  def isLogic(self) -> bool:
    return self._type == Operator.LOGIC

  @property
  def isCommand(self) -> bool:
    return self._type == Operator.COMMAND

  @property
  def isCommutatif(self) -> bool:
    return self._isCommutatif

  @property
  def regex(self) -> str:
    return self._regex

  @property
  def symbol(self) -> str:
    return self._symbol

  @property
  def arity(self) -> int:
    return self._arity

  @property
  def priority(self) -> int:
    return self._priority

  def __init__(self, arity:int, isCommutatif:bool, regex:str, symbol:str, optype:int, priority:int):
    self._arity         = arity
    self._isCommutatif  = isCommutatif
    self._regex         = regex
    self._symbol        = symbol
    self._type          = optype
    self._priority      = priority

  def __str__(self) -> str:
    return self._symbol

class Operators:
  ADD     : Operator = Operator(2, True , r"\+" , "+"  , Operator.ARITHMETIC, 5)
  MINUS   : Operator = Operator(2, False, r"\-" , "-"  , Operator.ARITHMETIC, 5)
  MULT    : Operator = Operator(2, True , r"\*" , "*"  , Operator.ARITHMETIC, 7)
  DIV     : Operator = Operator(2, False, r"\/" , "/"  , Operator.ARITHMETIC, 7)
  MOD     : Operator = Operator(2, False, "%"  , "%"  , Operator.ARITHMETIC, 8)
  NEG     : Operator = Operator(1, False, ""   , "-"  , Operator.ARITHMETIC, 6)
  OR      : Operator = Operator(2, True , r"\|" , "|"  , Operator.ARITHMETIC, 6)
  AND     : Operator = Operator(2, True , "&"  , "&"  , Operator.ARITHMETIC, 7)
  XOR     : Operator = Operator(2, True , r"\^" , "^"  , Operator.ARITHMETIC, 7)
  INVERSE : Operator = Operator(1, False, r"\~" , "~"  , Operator.ARITHMETIC, 6)
  SUP     : Operator = Operator(2, False, ">"  , ">"  , Operator.COMPARAISON, 4)
  SUPOREQ : Operator = Operator(2, False, ">=" , ">=" , Operator.COMPARAISON, 4)
  INF     : Operator = Operator(2, False, "<"  , "<"  , Operator.COMPARAISON, 4)
  INFOREQ : Operator = Operator(2, False, "<=" , "<=" , Operator.COMPARAISON, 4)
  EQ      : Operator = Operator(2, True , "=="  , "==", Operator.COMPARAISON, 4)
  NOTEQ   : Operator = Operator(2, True , "!="  , "!=", Operator.COMPARAISON, 4)
  LOGICOR : Operator = Operator(2, True , "or" , "or" , Operator.LOGIC , 1)
  LOGICAND: Operator = Operator(2, True , "and", "and", Operator.LOGIC , 3)
  LOGICNOT: Operator = Operator(1, False, "not", "not", Operator.LOGIC , 2)
  SWAP    : Operator = Operator(2, False, ""   ,"swap", Operator.OTHER, 0)
  MOVE    : Operator = Operator(1, False, ""   ,"move", Operator.COMMAND, 0)
  HALT    : Operator = Operator(0, False, ""   ,"halt", Operator.COMMAND, 0)
  NOP     : Operator = Operator(0, False, ""   ,"nop", Operator.COMMAND, 0)
  GOTO    : Operator = Operator(1, False, ""   ,"goto", Operator.COMMAND, 0)
  LOAD    : Operator = Operator(1, False, ""   ,"load", Operator.COMMAND, 0)
  STORE   : Operator = Operator(1, False, ""   ,"store", Operator.COMMAND, 0)
  CMP     : Operator = Operator(2, False, ""   ,"cmp" , Operator.COMMAND, 0)
  PRINT   : Operator = Operator(1, False, ""   ,"print", Operator.COMMAND, 0)
  INPUT   : Operator = Operator(1, False, ""   ,"input", Operator.COMMAND, 0)

  @classmethod
  def list(cls) -> List[Operator]:
    return [
      cls.ADD,
      cls.MINUS,
      cls.MULT,
      cls.DIV,
      cls.MOD,
      cls.NEG,
      cls.OR,
      cls.AND,
      cls.XOR,
      cls.INVERSE,
      cls.SUP,
      cls.SUPOREQ,
      cls.EQ,
      cls.INF,
      cls.INFOREQ,
      cls.NOTEQ,
      cls.LOGICOR,
      cls.LOGICAND,
      cls.LOGICNOT,
      cls.SWAP,
      cls.MOVE,
      cls.HALT,
      cls.NOP,
      cls.GOTO,
      cls.LOAD,
      cls.STORE,
      cls.CMP,
      cls.PRINT,
      cls.INPUT
    ]

  @classmethod
  def expressionBinaryOps(cls) -> List[Operator]:
    return [op for op in cls.list() if op.arity == 2]
  
  @classmethod
  def expressionUnaryOps(cls) -> List[Operator]:
    return [op for op in cls.list() if op.arity == 1]