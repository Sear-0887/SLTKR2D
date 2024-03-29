# to add a binary operator:
# add it to ops
# add a case in apply()

# to add an unary operator:
# add it to the uops list
# add a case in applyuop()

# to add a postfix operator:
# add it to the pops list
# add a case in applypop()

import re
import math

uops = ['-']
pops=['!']

NUM   = 'NUM'   # Token: number
LPAR  = 'LPAR'  # Token: left paren
RPAR  = 'RPAR'  # Token: right paren
OP    = 'OP'    # Token: binary operator
UOP   = 'UOP'   # Token: unary operator
SYM   = 'SYM'   # Token: symbol (variable or function)
EXPR  = 'EXPR'  # Token: expression (output of evaluate)
CALL  = 'CALL'  # Token: left paren after function name
POP   = 'POP'   # Token: postfix operator
LEFT  = 'LEFT'  # associativity: left
RIGHT = 'RIGHT' # associativity: right

ops={
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

symbols={
  'φ'  : (1 + 5 ** 0.5) / 2,
  'phi': (1 + 5 ** 0.5) / 2,
  'pi' : math.pi,
  'π'  : math.pi,
  'e'  : math.e,
  'i'  : 1j,
}

def mypow(a,b):
  if b>100000: # or maybe timeout
    raise TimeoutError([a, b])
  return a**b

def applyop(op,v1,v2):
  print(op, v1, v2)
  # apply op to v1 and v2
  # remember, they are all [type,value] pairs
  if v1[0] != NUM or v2[0] != NUM:
    return [EXPR, op[1], v1, v2]
  if op[1] == '+':
    return [NUM, v1[1]+v2[1]]
  if op[1] == '-':
    return [NUM, v1[1]-v2[1]]
  if op[1] == '*':
    return [NUM, v1[1]*v2[1]]
  if op[1] == '/':
    return [NUM, v1[1]/v2[1]]
  if op[1] == '^' or op[1] == '**':
    return [NUM, mypow(v1[1],v2[1])]
  if op[1] == '%' or op[1] == 'mod':
    return [NUM, v1[1]%v2[1]]
  if op[1] == '//' or op[1] == 'div':
    return [NUM, v1[1]//v2[1]]
  raise KeyError(["binary", op[1]])

def applyuop(op,v):
  # apply op to v
  # remember, they are both [type,value] pairs
  if v[0] != NUM:
    return [EXPR, op[1], v]
  if op[1] == '-':
    return [NUM, -v[1]]
  raise KeyError(["unary", op[1]])

def applypop(op,v):
  # apply op to v
  # remember, they are both [type,value] pairs
  if v[0]!=NUM:
    return [EXPR,op[1],v]
  if op[1]=='!':
    return [NUM,math.factorial(v[1])]
  raise KeyError(["postfix", op[1]])

def applyfunc(f,v):
  print(f, v)
  if v[0]!=NUM:
    return [EXPR,'(',f,v]
  if f=='log':
    return [NUM,math.log(v[1],10)]
  if f=='ln':
    return [NUM,math.log(v[1])]
  if f=='sqrt' or f=='√':
    return [NUM,math.sqrt(v[1])]
  if f=='asin' or f == 'arcsin':
    return [NUM,math.asin(v[1])]
  if f=='acos' or f == 'arccos':
    return [NUM,math.acos(v[1])]
  if f=='atan' or f == 'arctan':
    return [NUM, math.atan(v[1])]
  if f=='degree' or f=='deg':
    return [NUM, math.degrees(v[1])]
  if f=='radian' or f=='rad':
    return [NUM, math.radians(v[1])]
  if f=='sin':
    return [NUM,math.sin(v[1])]
  if f=='cos':
    return [NUM,math.cos(v[1])]
  if f=='tan':
    return [NUM,math.tan(v[1])]
  return [EXPR,'(',f,v]

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

def getNum(s):
  # an actual number
  # not a variable
  m=re.match(Floatnumber,s)
  if m:
    return float(s[:m.end()]),s[m.end():]
  m=re.match(Intnumber,s)
  if m:
    return int(s[:m.end()], base=0),s[m.end():] # Open to python to inter. the base
  return None,s

def getSym(s):
  # a symbol
  m=re.match('[a-zA-Z][a-zA-Z0-9]*',s)
  if m:
    return s[:m.end()],s[m.end():]
  for symbol in symbols:
    if s[0]==symbol:
      return symbol,s[1:]
  return None,s

def moreTokens(s):
  # are there more tokens?
  return s.strip()!=''

def getToken(s,lastType):
  # get one token
  # types accepted depand on last token
  # for example, can't have op after lpar
  ss=s.lstrip()
  if lastType in [NUM,SYM,RPAR,POP]:
    for pop in pops:
      if ss.startswith(pop):
        return [POP,pop],ss[len(pop):]
    for op in ops:
      if ss.startswith(op):
        return [OP,op],ss[len(op):]
    if ss.startswith(')'):
      return [RPAR],ss[1:]
    if lastType==SYM:
      if ss.startswith('('):
        return [CALL],ss[1:]
    raise ArithmeticError(s)
  if lastType in [LPAR,CALL,OP,UOP]:
    if ss.startswith('('):
      return [LPAR],ss[1:]
    for uop in uops:
      if ss.startswith(uop):
        return [UOP,uop],ss[len(uop):]
    num,snew=getNum(ss)
    if num is not None:
      return [NUM,num],snew
    sym,snew=getSym(ss)
    if sym is not None:
      return [SYM,sym],snew
    raise ArithmeticError(s)

def precedence(token):
  # get the precedence of a binary operator
  return ops[token[1]][0]

def rightassoc(op):
  return ops[op][1]==RIGHT

def leftassoc(op):
  return ops[op][1]==LEFT

def evaluate(expr):
  values=[]
  ops=[]

  s=expr

  # basic shunting yard parser
  lastType=OP # a valid expression can always come after an operator
  while moreTokens(s): # parse all the tokens
    #print('s1',s)
    #print('o1',ops)
    #print('v1',values)
    token,s=getToken(s,lastType)
    if token[0] in [NUM,SYM]: # number or symbol token
      values.append(token)
    if token[0] in [NUM,SYM,EXPR]: # number, symbol, or expression
      while len(ops)>0 and ops[-1][0]==UOP: # apply all unary operators on the stack
        op=ops[-1]
        ops=ops[:-1]
        values[-1]=applyuop(op,values[-1])
    if token[0]==LPAR: # left paren
      ops.append(token)
    if token[0]==CALL: # left paren of function
      ops.append(token)
    else:
      if len(values)>0 and values[-1][0]==SYM:
        if values[-1][1] in symbols:
          values[-1]=[NUM,symbols[values[-1][1]]]
    if token[0]==UOP: # unary operator
      ops.append(token)
    if token[0]==POP: # postfix operator
      values[-1]=applypop(token,values[-1])
    if token[0]==RPAR: # right paren
      while ops[-1][0] not in [LPAR,CALL]: # finish the parenthesized expression
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(applyop(op,v1,v2))
      if ops[-1][0]==CALL:
        v1,v2=values[-2:]
        values=values[:-2]
        assert v1[0]==SYM # the function should always be a symbol
        values.append(applyfunc(v1[1],v2))
      ops=ops[:-1] # pop the left paren as well
      while len(ops)>0 and ops[-1][0]==UOP: # apply all unary operators on the stack
        op=ops[-1]
        ops=ops[:-1]
        values[-1]=applyuop(op,values[-1])
    if token[0]==OP:
      while len(ops)>0 and ops[-1][0] not in [LPAR,CALL] and (precedence(ops[-1])>precedence(token) or (precedence(ops[-1])==precedence(token) and leftassoc(ops[-1][1]))):
        # apply all operators to the left with a lower precedence
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(applyop(op,v1,v2))
      ops.append(token) # push this operator
    lastType=token[0] # type of last token
    #print('s',s)
    #print('o',ops)
    #print('v',values)
  while len(ops)>0: # apply the rest of the operators
    op=ops[-1]
    ops=ops[:-1]
    v1,v2=values[-2:]
    values=values[:-2]
    values.append(applyop(op,v1,v2))
  if len(values)>1: # each operator reduces the number of values by 1
    raise ValueError('Not enough operators')
  if len(values)==0: # how
    raise ValueError('Empty expression')
  return values[0]

def stringifyexpr(e):
  # convert an expr from evaluate to a string, so evaluate on that string will probably give back the same expr
  if e[0] in [SYM,NUM]:
    return str(e[1])
  if e[1]=='(':
    return f'{e[2]}({",".join(map(stringifyexpr,e[3:]))})'
  if len(e) == 3:
    if len(e[2]) == 4:
      return f'{e[1]}({stringifyexpr(e[2])})' # -(a+b)
    return f'{e[1]}{stringifyexpr(e[2])}' # a
  if len(e) == 4:
    _,op,left,right = e
    p1 = precedence(e)
    pleft = precedence(left) if left[0] in [OP,EXPR] else math.inf
    pright = precedence(right) if right[0] in [OP,EXPR] else math.inf
    leftparen = pleft<p1 or (pleft==p1 and rightassoc(op))
    rightparen = pright<p1 or (pright==p1 and leftassoc(op))
    sleft=stringifyexpr(left)
    if leftparen:
      sleft=f'({sleft})'
    sright=stringifyexpr(right)
    if rightparen:
      sright=f'({sright})'
    return f'{sleft}{op}{sright}'