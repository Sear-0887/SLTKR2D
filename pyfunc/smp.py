def strip(s):
    s=s.lstrip()
    while len(s)>0 and s[0]=='#':
        s=(s.split('\n',maxsplit=1)+[''])[1].lstrip()
    return s

def _smptostr(smp,indented,indent):
    if type(smp) in [str,int]:
        return str(smp),False # do not add newlines around
    if type(smp) is list:
        s=''
        for x in smp:
            xs,xnl=_smptostr(x,indented+indent,indent)
            nl=f'\n{indented}' if xnl else ''
            s+=f'\n{indented}[{xs}{nl}]'
        return s,True
    if type(smp) is dict:
        s=''
        for k,v in smp.items():
            xs,xnl=_smptostr(v,indented+indent,indent)
            nl=f'\n{indented}' if xnl else ''
            s+=f'\n{indented}{{{k}}}:{{{xs}{nl}}}'
        return s,True

def smptostr(smp,indent='  '):
    return _smptostr(smp,'',indent)[0].lstrip('\n')

def _getword(s):
    s=strip(s)
    i=0
    while i<len(s) and s[i]!='}' and s[i]!=']':
        i=i+1
    return s[i:],s[:i]

def _geterrmessage(err,sinit,s):
    lines=sinit[:len(sinit)-len(s)].split('\n')
    line=len(lines)
    col=len(lines[-1])
    return f'Error at line {line}, column {col}: {err}'

def _getsmpvalue(sinit):
    s=strip(sinit)
    if s.startswith('['):
        # list
        l=[]
        s1=s
        while s1.startswith('['):
            s2=s1[1:]
            s3,v=_getsmpvalue(s2)
            l.append(v)
            assert strip(s3).startswith(']'),_geterrmessage('missing ]',sinit,s3)
            s1=strip(strip(s3)[1:])
        return s1,l
    elif s.startswith('{'):
        # dict
        d={}
        s1=s
        while s1.startswith('{'):
            s2=s1[1:]
            s3,k=_getword(s2)
            assert strip(s3).startswith('}'),_geterrmessage('missing }',sinit,s3)
            s4=strip(strip(s3)[1:])
            assert s4.startswith(':'),_geterrmessage('missing :',sinit,s4)
            s5=strip(s4[1:])
            assert s5.startswith('{'),_geterrmessage('missing {',sinit,s5)
            s6=s5[1:]
            s7,v=_getsmpvalue(s6)
            assert strip(s7).startswith('}'),_geterrmessage('missing }',sinit,s7)
            s1=strip(strip(s7)[1:])
            d[k]=v
        return s1,d
    else:
        # string
        s2,w=_getword(s)
        return s2,w.strip()

def getsmpvalue(s):
    # read an smp into a python object
    return _getsmpvalue(s)[1]