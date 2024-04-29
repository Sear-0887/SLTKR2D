import re
import collections
import pyfunc.smp as smp
import glob
from pyfunc.datafunc import capitalize, plural, past
from pyfunc.lang import cfg
idtoblock = {}

blockinfos = collections.defaultdict(dict)

locale = {}

modifiers={
    '^':capitalize,
    's':plural,
    'd':past,
}

def getblockids():
    with open(cfg("localGame.texture.blockIDFile"), encoding="utf-8") as f:
        data=smp.getsmpvalue(f.read())
    for name,i in data.items():
        blockinfos[name]["id"] = int(i)
        idtoblock[int(i)] = name

def geticoncoords():
    with open(cfg("localGame.texture.iconLocationFile"), encoding="utf-8") as f:
        data=smp.getsmpvalue(f.read())
    for icon,xy in data.items():
        x,y=xy.split(',')
        blockinfos[icon]["iconcoord"] = (int(x), int(y))

def substitutelocale(s):
    # substitute locale entries into others
    # used in descriptions
    # a reference is {category name|mods}
    # mods is optional and is a string containing one or more of ^, s, or d
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
    # get locale entries from config.local_game.language_path
    # a locale entry is
    # category name = value
    # value can be continued across lines with a backslash (\)
    # comments beginning with # are ignored
    for langname, langdata in cfg("localGame.language").items():
        langpath=langdata['path']
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

def assetinit():
    getblockids()
    geticoncoords()
    getlocale()
