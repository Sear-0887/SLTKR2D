# to add a binary operator:
# add it to the ops list
# add it to precedences
# add a case in apply()

# to add an unary operator:
# add it to the uops list
# add a case in applyuop()

import math

ops=['+','-','*','/','^']

uops=['-']

precedences={
  '+':2,
  '-':2,
  '*':3,
  '/':3,
  '^':1,
}

NUM='NUM'
LPAR='LPAR'
RPAR='RPAR'
OP='OP'
UOP='UOP'
SYM='SYM'
EXP='EXP'

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

import re

def getNum(s):
  # an actual number
  # not a variable
  m=re.match(Floatnumber,s)
  if m:
    return float(s[:m.end()]),s[m.end():]
  m=re.match(Intnumber,s)
  if m:
    return int(s[:m.end()]),s[m.end():]
  return None,s

symbols='πe'

def getSym(s):
  # a symbol
  m=re.match('[a-zA-Z][0-9]*',s)
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
  if lastType in [NUM,SYM,RPAR]:
    for op in ops:
      if ss.startswith(op):
        return [OP,op],ss[len(op):]
    if ss.startswith(')'):
      return [RPAR],ss[1:]
    raise Exception('no token: '+s)
  if lastType in [LPAR,OP,UOP]:
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
    raise Exception('no token: '+s)

def apply(op,v1,v2):
  # apply op to v1 and v2
  # remember, they are all [type,value] pairs
  if v1[0]!=NUM or v2[0]!=NUM:
    return [EXP,op[1],v1,v2]
  if op[1]=='+':
    return [NUM,v1[1]+v2[1]]
  if op[1]=='-':
    return [NUM,v1[1]-v2[1]]
  if op[1]=='*':
    return [NUM,v1[1]*v2[1]]
  if op[1]=='/':
    return [NUM,v1[1]/v2[1]]
  if op[1]=='^':
    return [NUM,v1[1]**v2[1]]
  raise Exception('unrecognized binary operator '+op[1])

def applyuop(op,v):
  # apply op to v
  # remember, they are both [type,value] pairs
  if v[0]!=NUM:
    return [EXP,op[1],v]
  if op[1]=='-':
    return [NUM,-v[1]]
  raise Exception('unrecognized unary operator '+op[1])

def precedence(token):
  # get the precedence of a binary operator
  return precedences[token[1]]

def rightassoc(op):
  return False

def leftassoc(op):
  return True

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
    if token[0] in [NUM,SYM,EXP]: # number, symbol, or expression
      while len(ops)>0 and ops[-1][0]==UOP: # apply all unary operators on the stack
        op=ops[-1]
        ops=ops[:-1]
        values[-1]=applyuop(op,values[-1])
    if token[0]==LPAR: # left paren
      ops.append(token)
    if token[0]==UOP: # unary operator
      ops.append(token)
    if token[0]==RPAR: # right paren
      while ops[-1][0]!=LPAR: # finish the parenthesized expression
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(apply(op,v1,v2))
      ops=ops[:-1] # pop the left paren as well
    if token[0]==OP:
      while len(ops)>0 and ops[-1][0]!=LPAR and precedence(ops[-1])>=precedence(token):
        # apply all operators to the left with a lower precedence
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(apply(op,v1,v2))
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
    values.append(apply(op,v1,v2))
  if len(values)>1: # each operator reduces the number of values by 1
    raise Exception('not enough operators')
  if len(values)==0: # how
    raise Exception('empty expression')
  return values[0]

def stringifyexpr(e):
  if e[0] in [SYM,NUM]:
    return str(e[1])
  if len(e)==3:
    if len(e[2])==4:
      return f'{e[1]}({stringifyexpr(e[2])})' # -(a+b)
    return f'{e[1]}{stringifyexpr(e[2])}' # a
  if len(e)==4:
    _,op,left,right=e
    p1=precedence(e)
    pleft=precedence(left) if left[0] in [OP,EXP] else math.inf
    pright=precedence(right) if right[0] in [OP,EXP] else math.inf
    leftparen=pleft<p1 or (pleft==p1 and rightassoc(op))
    rightparen=pright<p1 or (pright==p1 and leftassoc(op))
    sleft=stringifyexpr(left)
    if leftparen:
      sleft=f'({sleft})'
    sright=stringifyexpr(right)
    if rightparen:
      sright=f'({sright})'
    return f'{sleft}{op}{sright}'