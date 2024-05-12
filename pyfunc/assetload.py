import re
import collections
import pyfunc.smp as smp
import glob
from pyfunc.datafunc import capitalize, plural, past
from pyfunc.lang import opencfg, cfg
from typing import Any

idtoblock:dict[int, str] = {}

blockinfos:dict[str, dict[str, Any]] = collections.defaultdict(dict)

locale:dict[tuple[str, ...], str] = {}

modifiers={
    '^':capitalize,
    's':plural,
    'd':past,
}

blockdefregex = 'BLOCK_DEF\\((?P<name>[a-z_]+),(?P<collision>collision::[a-z_]+(\\|collision::[a-z_]+)*),(?P<attr>atb::[a-z_]+(\\|atb::[a-z_]+)*),0b(?P<weld>\\d\\d\\d\\d),(?P<weldtime>\\d+)\\)'
def getblockdefs() -> None:
    with opencfg("localGame.texture.blockDefsFile", encoding="utf-8") as f:
        data = f.read()
    for line in data.split('\n'):
        line = ''.join(line.split()) # remove spaces
        match = re.match(blockdefregex,line)
        if match is not None:
            name = match['name']
            collision1 = match['collision']
            collision2 = collision1.split('|')
            collision3 = [re.fullmatch('collision::(?P<name>[a-z_]+)',c) for c in collision2]
            collision = [c['name'] for c in collision3]
            attr1 = match['attr']
            attr2 = attr1.split('|')
            attr3 = [re.fullmatch('atb::(?P<name>[a-z_]+)',a) for a in attr2]
            attr = [a['name'] for a in attr3]
            weld = match['weld']
            weld = [s == '1' for s in weld]
            left,bottom,right,top = weld
            #weldtime = match['weldtime']
            blockinfos[name]['collision'] = collision
            blockinfos[name]['attributes'] = attr
            blockinfos[name]['weldablesides'] = top,left,bottom,right

def getblockids() -> None:
    with opencfg("localGame.texture.blockIDFile", encoding="utf-8") as f:
        data=smp.getsmpvalue(f.read())
    assert isinstance(data,dict)
    for name,i in data.items():
        assert isinstance(i,str)
        blockinfos[name]["id"] = int(i)
        idtoblock[int(i)] = name

def geticoncoords() -> None:
    with opencfg("localGame.texture.iconLocationFile", encoding="utf-8") as f:
        data=smp.getsmpvalue(f.read())
    assert isinstance(data,dict)
    for icon,xy in data.items():
        assert isinstance(xy,str)
        x,y=xy.split(',')
        blockinfos[icon]["iconcoord"] = (int(x), int(y))

def substitutelocale(s:str) -> str:
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

def getlocale() -> None:
    # get locale entries from config.local_game.language_path
    # a locale entry is
    # category name = value
    # value can be continued across lines with a backslash (\)
    # comments beginning with # are ignored
    langinfo = cfg("localGame.language")
    assert isinstance(langinfo,dict)
    for langname, langdata in langinfo.items():
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
                    tkey=tuple(key.split())
                    value=value.strip()
                    locale[tkey]=value

    for tkey,s in locale.items():
        locale[tkey]=substitutelocale(s)

def assetinit() -> None:
    getblockids()
    getblockdefs()
    geticoncoords()
    getlocale()
