# to add a binary operator:
# add it to ops
# add a case in apply()

# to add an unary operator:
# add it to the uops list
# add a case in applyuop()

# to add a postfix operator:
# add it to the pops list
# add a case in applypop()

import random
import re
import math
import cmath
import logging
import typing

l = logging.getLogger()

TokenType:typing.TypeAlias = (
  typing.Literal['NUM'] |
  typing.Literal['SYM'] |
  typing.Literal['EXPR'] |
  typing.Literal['LPAR'] |
  typing.Literal['CALL'] |
  typing.Literal['RPAR'] |
  typing.Literal['BOP'] |
  typing.Literal['UOP'] |
  typing.Literal['POP']
)

NUM:typing.Literal['NUM']    = 'NUM'   # Token: number
SYM:typing.Literal['SYM']    = 'SYM'   # Token: symbol (variable or function)
EXPR:typing.Literal['EXPR']  = 'EXPR'  # Token: expression (output of evaluate)

LPAR:typing.Literal['LPAR']  = 'LPAR'  # Token: left paren
CALL:typing.Literal['CALL']  = 'CALL'  # Token: left paren after function name
RPAR:typing.Literal['RPAR']  = 'RPAR'  # Token: right paren

BOP:typing.Literal['BOP']    = 'BOP'   # Token: binary operator
UOP:typing.Literal['UOP']    = 'UOP'   # Token: unary operator
POP:typing.Literal['POP']    = 'POP'   # Token: postfix operator

Assoc:typing.TypeAlias = typing.Literal['LEFT'] | typing.Literal['RIGHT']

LEFT:Assoc  = 'LEFT'  # Associativity: left
RIGHT:Assoc = 'RIGHT' # Associativity: right

Bop = typing.NewType('Bop',str)
BopToken:typing.TypeAlias = tuple[typing.Literal["BOP"],Bop]
Uop = typing.NewType('Uop',str)
UopToken:typing.TypeAlias = tuple[typing.Literal["UOP"],Uop]
Pop = typing.NewType('Pop',str)
PopToken:typing.TypeAlias = tuple[typing.Literal["POP"],Pop]
Sym = typing.NewType('Sym',str)
SymToken:typing.TypeAlias = tuple[typing.Literal["SYM"],Sym]
NumType:typing.TypeAlias = int | float | complex
NumToken:typing.TypeAlias = tuple[typing.Literal["NUM"],NumType]
ExprToken:typing.TypeAlias = (
  tuple[typing.Literal["EXPR"],Uop | Pop,'ValueToken'] | 
  tuple[typing.Literal["EXPR"],Bop,'ValueToken','ValueToken'] |
  tuple[typing.Literal["EXPR"],typing.Literal['('],'ValueToken','ValueToken']
)
ValueToken:typing.TypeAlias = SymToken | NumToken | ExprToken

LParToken:typing.TypeAlias = tuple[typing.Literal["LPAR"]]
CallToken:typing.TypeAlias = tuple[typing.Literal["CALL"]]

OpToken:typing.TypeAlias = BopToken | UopToken | PopToken | LParToken | CallToken

AnyToken:typing.TypeAlias = ValueToken | BopToken | UopToken | PopToken | LParToken | CallToken | tuple[typing.Literal["RPAR"]]

RealToken:typing.TypeAlias = SymToken | NumToken | BopToken | UopToken | PopToken | LParToken | CallToken | tuple[typing.Literal["RPAR"]]

prefixOperators:list[Uop] = [Uop('-')]
postfixOperators:list[Pop] = [Pop('!')]

binaryOperators:dict[Bop,tuple[int,Assoc]] = {
  Bop('//') : (5, LEFT ),
  Bop('div'): (5, LEFT ),
  Bop('%')  : (4, LEFT ),
  Bop('mod'): (4, LEFT ),
  Bop('**') : (3, RIGHT),
  Bop('^')  : (3, RIGHT),
  Bop('/')  : (2, LEFT ),
  Bop('*')  : (2, LEFT ),
  Bop('+')  : (1, LEFT ),
  Bop('-')  : (1, LEFT )
}

symbols:dict[Sym,NumType] = {
  Sym('φ')  : (1 + 5 ** 0.5) / 2,
  Sym('phi'): (1 + 5 ** 0.5) / 2,
  Sym('pi') : math.pi,
  Sym('π')  : math.pi,
  Sym('e')  : math.e,
  Sym('i')  : 1j,
}

def customPowerOperation(a:NumType,b:NumType) -> NumType:
  if abs(b)>100000: # or maybe timeout
    raise TimeoutError([a, b])
  return a**b

# apply operation to operand1 and operand2
# remember, they are all [type,value] pairs
def applyBinaryOperations(operation:BopToken, operand1:ValueToken, operand2:ValueToken) -> ValueToken:
  l.debug(f"Applying Binary {operation} to {operand1}, {operand2}")
  operationSymbol = operation[1]
  if operand1[0] != NUM:
    return (EXPR, operationSymbol, operand1, operand2)
  if operand2[0] != NUM:
    return (EXPR, operationSymbol, operand1, operand2)
  operand1Value = operand1[1]
  operand2Value = operand2[1]
  match operationSymbol:
    case '+':          return (NUM, operand1Value + operand2Value)
    case '-':          return (NUM, operand1Value - operand2Value)
    case '*':          return (NUM, operand1Value * operand2Value)
    case '/':          return (NUM, operand1Value / operand2Value)
    case '^'  | '**' : return (NUM, customPowerOperation(operand1Value,operand2Value))
    case '%'  | 'mod': return (NUM, operand1Value % operand2Value) # ype: ignore # just assume it won't have complex args
    case '//' | 'div': return (NUM, operand1Value // operand2Value) # ype: ignore # just assume it won't have complex a
    case _:            raise  KeyError(["binary", operationSymbol])

def applyPrefixOperation(operation:UopToken, operand:ValueToken) -> ValueToken:
  l.debug(f"Applying Prefix {operation} to {operand}")
  operationSymbol = operation[1]
  if operand[0] != NUM:
    return (EXPR, operationSymbol, operand)
  if operationSymbol == '-':
    return (NUM, -operand[1])
  raise KeyError(["unary", operationSymbol, operand[1]])

def applyPostfixOperation(operation:PopToken, operand:ValueToken) -> ValueToken:
  l.debug(f"Applying Postfix{operation} to {operand}")
  operationSymbol = operation[1]
  if operand[0] != NUM:
    return (EXPR, operationSymbol, operand)
  if operationSymbol=='!':
    # gamma function maybe?
    # math factorial takes int
    # cmath gamma?
    assert isinstance(operand[1],int)
    return (NUM, math.factorial(operand[1]))
  raise KeyError(["postfix", operationSymbol])

def applyFunction(functionName:str,operand:ValueToken) -> ValueToken:
  l.debug(f"Applying Function {functionName} to {operand}")
  if operand[0] != NUM:
    return typing.cast(ValueToken,(EXPR,'(',functionName,operand)) # for reasons
  operandValue = operand[1]
  match functionName:
    case 'log'            : return (NUM, cmath.log(operandValue, 10))
    case 'ln'             : return (NUM, cmath.log(operandValue))
    case 'sqrt' | '√'     : return (NUM, cmath.sqrt(operandValue))
    case 'asin' | 'arcsin': return (NUM, cmath.asin(operandValue))
    case 'acos' | 'arccos': return (NUM, cmath.acos(operandValue))
    case 'atan' | 'arctan': return (NUM, cmath.atan(operandValue))
    case 'degree' | 'deg' : return (NUM, math.degrees(operandValue))
    case 'radian' | 'rad' : return (NUM, math.radians(operandValue))
    case 'sin'            : return (NUM, cmath.sin(operandValue))
    case 'cos'            : return (NUM, cmath.cos(operandValue))
    case 'tan'            : return (NUM, cmath.tan(operandValue))
    case 'rdm'            : return (NUM, random.random()*operandValue)
    case _                : return typing.cast(ValueToken,(EXPR,'(',functionName,operand))
# here starts RbCaVi's code
# please know what you are doing, sear.

# from cpython Tokenize.py
def group(*choices:str) -> str: return '(' + '|'.join(choices) + ')'
def maybe(*choices:str) -> str: return group(*choices) + '?'

Hexnumber = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber = r'0[bB](?:_?[01])+'
Octnumber = r'0[oO](?:_?[0-7])+'
Decnumber = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat = group(r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
                   r'\.[0-9](?:_?[0-9])*') + maybe(Exponent)
Expfloat = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Number = group(Floatnumber, Intnumber)
# end from cpython Tokenize.py

def getANumber(expression:str) -> tuple[int | float | None, str]:
  # Get an actual number, not a variable or symbol
  if matched := re.match(Floatnumber, expression):
    return float(expression[:matched.end()]), expression[matched.end():]
  if matched := re.match(Intnumber, expression):
    # Open to python to inter. the base
    return int(expression[:matched.end()], base=0), expression[matched.end():]
  return None,expression

def getASymbol(expression:str) -> tuple[Sym | None, str]:
  # Get a actual symbol, not a variable or number
  if m := re.match('[a-zA-Z][a-zA-Z0-9]*',expression):
    return typing.cast(Sym,expression[:m.end()]),expression[m.end():]
  for symbol in symbols:
    if expression[0]==symbol:
      return symbol,expression[1:]
  return None,expression

def ifMoreTokens(expression:str) -> bool:
  # are there more tokens?
  return expression.strip() != ''

def getToken(ss:str,lastType:TokenType) -> tuple[RealToken,str]:
  # get one token
  # the types accepted depends on the last token
  # for example, you can't have a binary operator after (
  ss=ss.lstrip()
  if lastType in [NUM,SYM,RPAR,POP]:
    for pfoperator in postfixOperators:
      if ss.startswith(pfoperator):
        return (POP,pfoperator) ,ss[len(pfoperator):]
    for op in binaryOperators:
      if ss.startswith(op):
        return (BOP,op),ss[len(op):]
    if ss.startswith(')'):
      return (RPAR,),ss[1:]
    if lastType==SYM:
      if ss.startswith('('):
        return (CALL,),ss[1:]
    raise ArithmeticError(ss)
  if lastType in [LPAR,CALL,BOP,UOP]:
    if ss.startswith('('):
      return (LPAR,),ss[1:]
    for uop in prefixOperators:
      if ss.startswith(uop):
        return (UOP,uop),ss[len(uop):]
    num,snew=getANumber(ss)
    if num is not None:
      return (NUM,num),snew
    sym,snew=getASymbol(ss)
    if sym is not None:
      return (SYM,sym),snew
    raise ArithmeticError(ss)
  if lastType == EXPR:
    raise ArithmeticError([ss,'how did an expr get here?'])
  raise ArithmeticError([ss,'what other type is there?'])

def getPrecedenceOfOperator(token:BopToken) -> int:
  # get the precedence of a binary operator
  return binaryOperators[token[1]][0]

def rightassoc(op:Bop) -> bool:
  return binaryOperators[op][1]==RIGHT

def leftassoc(op:Bop) -> bool:
  return binaryOperators[op][1]==LEFT

def evaluate(originalExpression:str) -> ValueToken:
  valueStack:list[ValueToken] = []
  operatorStack:list[OpToken] = []

  expression = originalExpression

  # basic shunting yard parser
  lastType:TokenType = BOP # a valid expression can always come after an operator
  while ifMoreTokens(expression): # parse all the tokens
    token, expression = getToken(expression,lastType)
    # token[0] is the type of the token
    if token[0] == NUM or token[0] == SYM: # number or symbol token
      valueStack.append(token)
      while len(operatorStack) > 0 and operatorStack[-1][0] == UOP: # apply all unary operators on the stack
        lastoperator = operatorStack.pop()
        assert lastoperator[0] == UOP # mypy thing
        valueStack[-1] = applyPrefixOperation(lastoperator,valueStack[-1])
    if token[0]==LPAR: # left paren
      operatorStack.append(token)
    if token[0]==CALL: # left paren of function
      operatorStack.append(token)
    else:
      # if the top of the stack is a symbol and not used as a function, replace it with its number value
      if len(valueStack)>0 and valueStack[-1][0]==SYM:
        if valueStack[-1][1] in symbols:
          valueStack[-1]=(NUM,symbols[valueStack[-1][1]])
    if token[0]==UOP: # unary operator
      operatorStack.append(token)
    if token[0]==POP: # postfix operator
      valueStack[-1]=applyPostfixOperation(token,valueStack[-1])
    if token[0]==RPAR: # right paren
      while operatorStack[-1][0] not in [LPAR,CALL]: # finish the parenthesized expression
        lastoperator = operatorStack.pop()
        assert lastoperator[0] == BOP # might not be a mypy thing
        operand1 = valueStack.pop()
        operand2 = valueStack.pop()
        valueStack.append(applyBinaryOperations(lastoperator, operand1, operand2))
      if operatorStack[-1][0]==CALL:
        operand1 = valueStack.pop()
        operand2 = valueStack.pop()
        assert operand1[0]==SYM # the function should always be a symbol
        valueStack.append(applyFunction(operand1[1],operand2))
      operatorStack.pop()
      while len(operatorStack)>0 and operatorStack[-1][0]==UOP: # apply all unary operators on the stack
        lastoperator = operatorStack.pop()
        assert lastoperator[0] == UOP # mypy thing
        valueStack[-1]=applyPrefixOperation(lastoperator,valueStack[-1])
    if token[0]==BOP:
      assert operatorStack[-1][0] == BOP
      while (
        len(operatorStack) > 0 and 
        operatorStack[-1][0] not in [LPAR,CALL] and 
        (
          getPrecedenceOfOperator(operatorStack[-1])>getPrecedenceOfOperator(token) or 
          (
            getPrecedenceOfOperator(operatorStack[-1]) == getPrecedenceOfOperator(token) and 
            leftassoc(operatorStack[-1][1])
          )
          )
        ):
        # apply all operators to the left with a lower precedence
        lastoperator = operatorStack.pop()
        assert lastoperator[0] == BOP # mypy thing
        assert operatorStack[-1][0] == BOP # just in case an uop gets in somehow
        operand1 = valueStack.pop()
        operand2 = valueStack.pop()
        valueStack.append(applyBinaryOperations(lastoperator,operand1,operand2))
      operatorStack.append(token) # push this operator
    lastType = token[0] # type of last token

  # No more tokens found then:
  while len(operatorStack) > 0: # apply the rest of the operators
    lastoperator = operatorStack.pop()
    assert lastoperator[0] == BOP # mypy thing
    operand1 = valueStack.pop()
    operand2 = valueStack.pop()
    valueStack.append(applyBinaryOperations(lastoperator,operand1,operand2))
  if len(valueStack) > 1: # each operator reduces the number of values by 1
    raise ValueError('Not enough operators to finish operation')
  if len(valueStack) == 0: # empty expression passed in
    raise ValueError('Empty expression')
  return valueStack[0]

def stringifyexpr(expression:ValueToken) -> str:
  # convert an expr from evaluate to a string, so evaluate on that string will probably give back the same expr
  if expression[0] == NUM or expression[0] == SYM:
    return str(expression[1])
  assert expression[0] == EXPR
  if expression[1]=='(':
    return f'{expression[2]}({stringifyexpr(expression[3])})'
  assert expression[1] != '('
  if len(expression) == 3: # (EXPR,Uop/Pop,arg)
    if len(expression[2]) == 4:
      return f'{expression[1]}({stringifyexpr(expression[2])})' # -(a+b)
    return f'{expression[1]}{stringifyexpr(expression[2])}' # a
  if len(expression) == 4:
    _,op,left,right = expression
    op = typing.cast(Bop,op) # mypy issue (probably a bug)
    p1 = getPrecedenceOfOperator((BOP,op))
    def getPrecedence(e:ValueToken) -> float: # i would use int | typing.Literal[math.inf] but that's not allowed
      if e[0] == EXPR:
        if len(e)==4 and e[1]!='(':
          return getPrecedenceOfOperator((BOP,e[1]))
      return math.inf
    pleft = getPrecedence(left)
    pright = getPrecedence(right)
    leftparen = pleft<p1 or (pleft==p1 and rightassoc(op))
    rightparen = pright<p1 or (pright==p1 and leftassoc(op))
    sleft=stringifyexpr(left)
    if leftparen:
      sleft=f'({sleft})'
    sright=stringifyexpr(right)
    if rightparen:
      sright=f'({sright})'
    return f'{sleft}{op}{sright}'
  raise ValueError('Invalid number of arguments')