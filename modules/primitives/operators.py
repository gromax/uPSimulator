"""
.. module:: operators
:synopsis: définit les symboles liés au différents opérateurs et leurs propriétés
"""

from typing import List

class Operator:
  _arity        :int
  _isCommutatif :bool
  _regex        :str
  _symbol       :str
  _isArithmetic :bool
  _isComparaison:bool
  _isLogic      :bool
  _priority     :int

  @property
  def isArithmetic(self) -> bool:
    return self._isArithmetic

  @property
  def isComparaison(self) -> bool:
    return self._isComparaison

  @property
  def isLogic(self) -> bool:
    return self._isLogic

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

  def __init__(self, arity:int, isCommutatif:bool, regex:str, symbol:str, isArithmetic:bool, isComparaison:bool, isLogic:bool, priority:int):
    self._arity         = arity
    self._isCommutatif  = isCommutatif
    self._regex         = regex
    self._symbol        = symbol
    self._isArithmetic  = isArithmetic
    self._isComparaison = isComparaison
    self._isLogic       = isLogic
    self._priority      = priority

  def __str__(self) -> str:
    return self._symbol

class Operators:
  ADD     : Operator = Operator(2, True , r"\+" , "+"  , True , False, False, 5)
  MINUS   : Operator = Operator(2, False, r"\-" , "-"  , True , False, False, 5)
  MULT    : Operator = Operator(2, True , r"\*" , "*"  , True , False, False, 7)
  DIV     : Operator = Operator(2, False, r"\/" , "/"  , True , False, False, 7)
  MOD     : Operator = Operator(2, False, "%"  , "%"  , True , False, False, 8)
  NEG     : Operator = Operator(1, False, ""   , "-"  , True , False, False, 6)
  OR      : Operator = Operator(2, True , r"\|" , "|"  , True , False, False, 6)
  AND     : Operator = Operator(2, True , "&"  , "&"  , True , False, False, 7)
  XOR     : Operator = Operator(2, True , r"\^" , "^"  , True , False, False, 7)
  INVERSE : Operator = Operator(1, False, r"\~" , "~"  , True , False, False, 6)
  SUP     : Operator = Operator(2, False, ">"  , ">"  , False, True , False, 4)
  SUPOREQ : Operator = Operator(2, False, ">=" , ">=" , False, True , False, 4)
  INF     : Operator = Operator(2, False, "<"  , "<"  , False, True , False, 4)
  INFOREQ : Operator = Operator(2, False, "<=" , "<=" , False, True , False, 4)
  EQ      : Operator = Operator(2, True , "=="  , "==", False, True , False, 4)
  NOTEQ   : Operator = Operator(2, True , "!="  , "!=", False, True , False, 4)
  LOGICOR : Operator = Operator(2, True , "or" , "or" , False, False, True , 1)
  LOGICAND: Operator = Operator(2, True , "and", "and", False, False, True , 3)
  LOGICNOT: Operator = Operator(1, False, "not", "not", False, False, True , 2)
  SWAP    : Operator = Operator(2, False, ""   ,"swap", False, False, False, 0)
  MOVE    : Operator = Operator(1, False, ""   ,"move", False, False, False, 0)
  HALT    : Operator = Operator(0, False, ""   ,"halt", False, False, False, 0)
  NOP     : Operator = Operator(0, False, ""   ,"nop", False, False, False, 0)
  GOTO    : Operator = Operator(1, False, ""   ,"goto", False, False, False, 0)
  LOAD    : Operator = Operator(1, False, ""   ,"load", False, False, False, 0)
  STORE   : Operator = Operator(1, False, ""   ,"store", False, False, False, 0)
  CMP     : Operator = Operator(2, False, ""   ,"cmp" , False, False, False, 0)
  PRINT   : Operator = Operator(1, False, ""   ,"print", False, False, False, 0)
  INPUT   : Operator = Operator(1, False, ""   ,"input", False, False, False, 0)

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