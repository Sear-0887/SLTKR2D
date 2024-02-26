ops=[*'+-*/^']

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

import re

def getNum(s):
  m=re.match(FloatNumber,s)
  if m:
    return float(s[:m.end()]),s[m.end():]
  m=re.match(IntNumber,s)
  if m:
    return int(s[:m.end()]),s[m.end():]
  return None,s

def moreTokens(s):
  return s.strip()!=''

def getToken(s,lastType):
  ss=s.lstrip()
  if lastType in [NUM,RPAR]:
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
    raise Exception('no token: '+s)

def apply(op,v1,v2):
  if op[1]=='+':
    return [NUM,v1[1]+v2[1]]
  if op[1]=='-':
    return [NUM,v1[1]-v2[1]]
  if op[1]=='*':
    return [NUM,v1[1]*v2[1]]
  if op[1]=='/':
    return [NUM,v1[1]/v2[1]]
  if op[1]=='^':
    return [NUM,v1[1]^v2[1]]
  raise Exception('unrecognized binary operator '+op[1])

def applyuop(op,v):
  if op[1]=='-':
    return [NUM,-v[1]]
  raise Exception('unrecognized unary operator '+op[1])

def precedence(token):
  return precedences[token[1]]

def evaluate(expr):
  values=[]
  ops=[]

  s=expr

  lastType=OP
  while moreTokens(s):
    token,s=getToken(s,lastType)
    #print(token,values,ops)
    if token[0]==NUM:
      values.append(token)
    if token[0]==NUM:
      while len(ops)>0 and ops[-1][0]==UOP:
        op=ops[-1]
        ops=ops[:-1]
        values[-1]=applyuop(op,values[-1])
    if token[0]==LPAR:
      ops.append(token)
    if token[0]==UOP:
      ops.append(token)
    if token[0]==RPAR:
      while ops[-1][0]!=LPAR:
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(apply(op,v1,v2))
      ops=ops[:-1]
    if token[0]==OP:
      while len(ops)>0 and ops[-1][0]!=LPAR and precedence(ops[-1])>=precedence(token):
        op=ops[-1]
        ops=ops[:-1]
        v1,v2=values[-2:]
        values=values[:-2]
        values.append(apply(op,v1,v2))
      ops.append(token)
    lastType=token[0]
  while len(ops)>0:
    op=ops[-1]
    ops=ops[:-1]
    v1,v2=values[-2:]
    values=values[:-2]
    values.append(apply(op,v1,v2))
  if len(values)>1:
    raise Exception('not enough operators')
  if len(values)==0:
    raise Exception('empty expression')
  return values[0]