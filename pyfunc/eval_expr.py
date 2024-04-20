import random
import re
import math

prefixOperators = ['-']
postfixOperators=['!']

NUM   = 'NUM'   # Token: number
LPAR  = 'LPAR'  # Token: left paren
RPAR  = 'RPAR'  # Token: right paren
BOP   = 'BOP'   # Token: binary operator
UOP   = 'UOP'   # Token: unary operator
SYM   = 'SYM'   # Token: symbol (variable or function)
EXPR  = 'EXPR'  # Token: expression (output of evaluate)
CALL  = 'CALL'  # Token: left paren after function name
POP   = 'POP'   # Token: postfix operator
LEFT  = 'LEFT'  # Associativity: left
RIGHT = 'RIGHT' # Associativity: right

binaryOperators = {
  '//' : (5, LEFT ),
  'div': (5, LEFT ),
  '%'  : (4, LEFT ),
  'mod': (4, LEFT ),
  '**' : (3, RIGHT),
  '^'  : (3, RIGHT),
  '/'  : (2, LEFT ),
  '*'  : (2, LEFT ),
  '+'  : (1, LEFT ),
  '-'  : (1, LEFT )
}

symbols = {
  'φ'  : (1 + 5 ** 0.5) / 2,
  'phi': (1 + 5 ** 0.5) / 2,
  'pi' : math.pi,
  'π'  : math.pi,
  'e'  : math.e,
  'i'  : 1j,
}

def customPowerOperation(a,b):
  if b>100000: # or maybe timeout
    raise TimeoutError([a, b])
  return a**b

# apply operation to operand1 and operand2
# remember, they are all [type,value] pairs
def applyBinaryOperations(operation, operand1, operand2):
  print(f"Applying {operation} to {operand1}, {operand2}")
  operationSymbol = operation[1]
  operand1Type, operand1Value = operand1[:2]
  operand2Type, operand2Value = operand2[:2]
  if operand1Type != NUM or operand2Type != NUM:
    return [EXPR, operationSymbol, operand1, operand2]
  match operationSymbol:
    case '+':          return [NUM, operand1Value + operand2Value]
    case '-':          return [NUM, operand1Value - operand2Value]
    case '*':          return [NUM, operand1Value * operand2Value]
    case '/':          return [NUM, operand1Value / operand2Value]
    case '^'  | '**' : return [NUM, customPowerOperation(operand1Value,operand2Value)]
    case '%'  | 'mod': return [NUM, operand1Value % operand2Value]
    case '//' | 'div': return [NUM, operand1Value // operand2Value]
    case _:            raise  KeyError(["binary", operationSymbol])

def applyPrefixOperation(operation, operand):
  print(f"Applying {operation} to {operand}")
  operationSymbol = operation[1]
  operandType, operandValue = operand
  if operandType != NUM:
    return [EXPR, operationSymbol, operandValue]
  if operationSymbol == '-':
    return [NUM, -operandValue]
  raise KeyError(["unary", operandValue])

def applyPostfixOperation(operation, operand):
  print(f"Applying {operation} to {operand}")
  operationSymbol = operation[1]
  operandType, operandValue = operand[:2]
  if operandType != NUM:
    return [EXPR, operationSymbol, operand]
  if operationSymbol=='!':
    return [NUM, math.factorial(operandValue)]
  raise KeyError(["postfix", operationSymbol])

def applyFunction(functionName,operand):
  print(functionName, operand)
  operandType, operandValue = operand[:2]
  if operandType != NUM:
    return [EXPR,'(',functionName,operand]
  match functionName:
    case 'log'            : return [NUM, math.log(operandValue, 10)]
    case 'ln'             : return [NUM, math.log(operandValue)]
    case 'sqrt' | '√'     : return [NUM, math.sqrt(operandValue)]
    case 'asin' | 'arcsin': return [NUM, math.asin(operandValue)]
    case 'acos' | 'arccos': return [NUM, math.acos(operandValue)]
    case 'atan' | 'arctan': return [NUM, math.atan(operandValue)]
    case 'degree' | 'deg' : return [NUM, math.degrees(operandValue)]
    case 'radian' | 'rad' : return [NUM, math.radians(operandValue)]
    case 'sin'            : return [NUM, math.sin(operandValue)]
    case 'cos'            : return [NUM, math.cos(operandValue)]
    case 'tan'            : return [NUM, math.tan(operandValue)]
    case 'rdm'            : return [NUM, random.random()*operandValue]
    case _                : return [EXPR,'(',functionName,operand]
# here starts RbCaVi's code
# please know what you are doing, sear.

# from cpython Tokenize.py
def group(*choices): return '(' + '|'.join(choices) + ')'
def maybe(*choices): return group(*choices) + '?'

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

def getANumber(expression):
  # Get an actual number, not a variable or symbol
  if matched := re.match(Floatnumber, expression):
    return float(expression[:matched.end()]), expression[matched.end():]
  if matched := re.match(Intnumber, expression):
    # Open to python to inter. the base
    return int(expression[:matched.end()], base=0), expression[matched.end():]
  return None,expression

def getASymbol(expression):
  # Get a actual symbol, not a variable or number
  if m := re.match('[a-zA-Z][a-zA-Z0-9]*',expression):
    return expression[:m.end()],expression[m.end():]
  for symbol in symbols:
    if expression[0]==symbol:
      return symbol,expression[1:]
  return None,expression

def ifMoreTokens(expression):
  # are there more tokens?
  return expression.strip() != ''

def getToken(ss,lastType):
  # get one token
  # the types accepted is depended on the last token
  # for example, you can't have a operator after (
  ss=ss.lstrip()
  if lastType in [NUM,SYM,RPAR,POP]:
    for pfoperator in postfixOperators:
      if ss.startswith(pfoperator):
        return [POP,pfoperator] ,ss[len(pfoperator):]
    for op in binaryOperators:
      if ss.startswith(op):
        return [BOP,op],ss[len(op):]
    if ss.startswith(')'):
      return [RPAR],ss[1:]
    if lastType==SYM:
      if ss.startswith('('):
        return [CALL],ss[1:]
    raise ArithmeticError(ss)
  if lastType in [LPAR,CALL,BOP,UOP]:
    if ss.startswith('('):
      return [LPAR],ss[1:]
    for uop in prefixOperators:
      if ss.startswith(uop):
        return [UOP,uop],ss[len(uop):]
    num,snew=getANumber(ss)
    if num is not None:
      return [NUM,num],snew
    sym,snew=getASymbol(ss)
    if sym is not None:
      return [SYM,sym],snew
    raise ArithmeticError(ss)

def getPrecedenceOfOperator(token):
  # get the precedence of a binary operator
  return binaryOperators[token[1]][0]

def rightassoc(op):
  return binaryOperators[op][1]==RIGHT

def leftassoc(op):
  return binaryOperators[op][1]==LEFT

def listparti(lst, index):
  # print(f"Partied {lst} to {lst[:index], lst[index:]}")
  if abs(index) == 1: # For single-isolated element
    return (lst[:index], lst[index])
  else:
    return (lst[:index], lst[index:])

def evaluate(originalExpression):
  valueStack = []
  operatorStack = []

  expression = originalExpression

  # basic shunting yard parser
  lastType=BOP # a valid expression can always come after an operator
  while ifMoreTokens(expression): # parse all the tokens
    token, expression = getToken(expression,lastType)
    tokenType = token[0]
    if tokenType in [NUM,SYM]: # number or symbol token
      valueStack.append(token)
    if tokenType in [NUM,SYM,EXPR]: # number, symbol, or expression
      while len(operatorStack) > 0 and operatorStack[-1][0] == UOP: # apply all unary operators on the stack
        operatorStack, lastoperator = listparti(operatorStack, -1)
        valueStack[-1] = applyPrefixOperation(lastoperator,valueStack[-1])
    if tokenType==LPAR: # left paren
      operatorStack.append(token)
    if tokenType==CALL: # left paren of function
      operatorStack.append(token)
    else:
      if len(valueStack)>0 and valueStack[-1][0]==SYM:
        if valueStack[-1][1] in symbols:
          valueStack[-1]=[NUM,symbols[valueStack[-1][1]]]
    if tokenType==UOP: # unary operator
      operatorStack.append(token)
    if tokenType==POP: # postfix operator
      valueStack[-1]=applyPostfixOperation(token,valueStack[-1])
    if tokenType==RPAR: # right paren
      while operatorStack[-1][0] not in [LPAR,CALL]: # finish the parenthesized expression
        operatorStack, lastoperator = listparti(operatorStack, -1)
        valueStack, operands = listparti(valueStack, -2)
        operand1, operand2 = operands
        valueStack.append(applyBinaryOperations(lastoperator, operand1, operand2))
      if operatorStack[-1][0]==CALL:
        valueStack, operands = listparti(valueStack, -2)
        operand1, operand2 = operands
        assert operand1[0]==SYM # the function should always be a symbol
        valueStack.append(applyFunction(operand1[1],operand2))
      operatorStack.pop()
      while len(operatorStack)>0 and operatorStack[-1][0]==UOP: # apply all unary operators on the stack
        operatorStack, lastoperator = listparti(operatorStack, -1)
        valueStack[-1]=applyPrefixOperation(lastoperator,valueStack[-1])
    if tokenType==BOP:
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
        operatorStack, lastoperator = listparti(operatorStack, -1)
        valueStack, operands = listparti(valueStack, -2)
        operand1, operand2 = operands
        valueStack.append(applyBinaryOperations(lastoperator,operand1,operand2))
      operatorStack.append(token) # push this operator
    lastType = tokenType # type of last token

  # No more tokens found then:
  while len(operatorStack) > 0: # apply the rest of the operators
    operatorStack, lastoperator = listparti(operatorStack, -1)
    valueStack, operands = listparti(valueStack, -2)
    print(f"{operands = }")
    operand1, operand2 = operands
    valueStack.append(applyBinaryOperations(lastoperator,operand1,operand2))
  if len(valueStack) > 1: # each operator reduces the number of values by 1
    raise ValueError('Not enough operators to finish operation')
  if len(valueStack) == 0: # empty expression passed in
    raise ValueError('Empty expression')
  return valueStack[0]

def stringifyexpr(expression):
  # convert an expr from evaluate to a string, so evaluate on that string will probably give back the same expr
  if expression[0] in [SYM,NUM]:
    return str(expression[1])
  if expression[1]=='(':
    return f'{expression[2]}({",".join(map(stringifyexpr,expression[3:]))})'
  if len(expression) == 3:
    if len(expression[2]) == 4:
      return f'{expression[1]}({stringifyexpr(expression[2])})' # -(a+b)
    return f'{expression[1]}{stringifyexpr(expression[2])}' # a
  if len(expression) == 4:
    _,op,left,right = expression
    p1 = getPrecedenceOfOperator(expression)
    pleft = getPrecedenceOfOperator(left) if left[0] in [BOP,EXPR] else math.inf
    pright = getPrecedenceOfOperator(right) if right[0] in [BOP,EXPR] else math.inf
    leftparen = pleft<p1 or (pleft==p1 and rightassoc(op))
    rightparen = pright<p1 or (pright==p1 and leftassoc(op))
    sleft=stringifyexpr(left)
    if leftparen:
      sleft=f'({sleft})'
    sright=stringifyexpr(right)
    if rightparen:
      sright=f'({sright})'
    return f'{sleft}{op}{sright}'