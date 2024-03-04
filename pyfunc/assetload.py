import re
import collections
import pyfunc.smp as smp
import glob
from pyfunc.lang import cfg, loadconfig

idtoblock = {}

blockinfos = collections.defaultdict(dict)

locale = {}

loadconfig()
lang = cfg("local_game","language_path")

def capitalize(s):
    s=s[0].upper()+s[1:]
    return s

def plural(s):
    if s.endswith('y'): # just in case
        s=s[:-1]+'ie'
    s+="s"
    return s

def past(s):
    if s.endswith('e'):
        s=s[:-1]
    s+="ed"
    return s

modifiers={
    '^':capitalize,
    's':plural,
    'd':past,
}

def getblockids():
    with open("assets/block_id_.smp") as f:
        data=smp.getsmpvalue(f.read())
    for name,i in data.items():
        blockinfos[name]["id"] = int(i)
        idtoblock[int(i)] = name

def geticoncoords():
    with open("assets/block_icons.smp") as f:
        data=smp.getsmpvalue(f.read())
    for icon,xy in data.items():
        x,y=xy.split(',')
        blockinfos[icon]["iconcoord"] = (int(x), int(y))

def substitutelocale(s):
    i=0 # the index to look for the next opening bracket at
    while '{' in s[i:]:
        i1=s.index('{',i)
        i2=s.find('}',i1)
        if i2==-1: # there is no closing bracket
            break
        p1=s[:i1]
        p2=s[i1+1:i2]
        p3=s[i2+1:]
        i=i1+1
        if '|' in p2:
            p2,modifier=p2.split('|',maxsplit=1)
        else:
            modifier=''
        key=tuple(part.strip() for part in p2.split())
        if key in locale:
            localized=locale[key]
            for mod in modifier:
                localized=modifiers[mod](localized)
            s=p1+localized+p3
    return s

def getlocale():
    for langname, langpath in lang.items():
        for fname in glob.glob(langpath):
            with open(fname, "r") as f:
                linesiter=iter(f)
                for line in linesiter:
                    while line.endswith('\\\n'):
                        line=line[:-2]+'\n'+next(linesiter) # add the next line to this if this line ends with a backslash
                    line=re.sub('#.*$','',line) # remove comments
                    if '=' not in line:
                        continue
                    key,value=line.split('=',maxsplit=1)
                    key=tuple(key.split())
                    value=value.strip()
                    locale[key]=value

    for key,s in locale.items():
        locale[key]=substitutelocale(s)

def init():
    getblockids()
    geticoncoords()
    getlocale()
