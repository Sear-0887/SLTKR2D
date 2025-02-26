import re
import collections
import pyfunc.smp as smp
import glob
from pyfunc.datafunc import capitalize, plural, past
from pyfunc.lang import openCfgPath, cfg
from typing import Any, cast, TypedDict

idtoblock:dict[int, str] = {}

blockinfos:dict[str, dict[str, Any]] = collections.defaultdict(dict)

globaLocale:dict[tuple[str, ...], str] = {}

class EntityData(TypedDict):
    texture: str

entities:dict[str, EntityData] = {}

modifiers={
    '^':capitalize,
    's':plural,
    'd':past,
}

blockdefregex = 'BLOCK_DEF\\((?P<name>[a-z_]+),(?P<collision>collision::[a-z_]+(\\|collision::[a-z_]+)*),(?P<attr>atb::[a-z_]+(\\|atb::[a-z_]+)*),0b(?P<weld>\\d\\d\\d\\d),(?P<weldtime>\\d+)\\)'
def getblockdefs() -> None:
    with openCfgPath("localGame.texture.blockDefsFile") as f:
        data = f.read()
    for line in data.split('\n'):
        line = ''.join(line.split()) # remove spaces
        match = re.match(blockdefregex,line)
        if match is not None:
            name = match['name']
            collision3 = [re.fullmatch('collision::(?P<name>[a-z_]+)',c) for c in match['collision'].split('|')]
            assert all(c is not None for c in collision3)
            collision = [c['name'] for c in cast(list[re.Match[str]],collision3)]
            attr3 = [re.fullmatch('atb::(?P<name>[a-z_]+)',a) for a in match['attr'].split('|')]
            assert all(a is not None for a in attr3)
            attr = [a['name'] for a in cast(list[re.Match[str]],attr3)]
            weld = match['weld']
            weld = [s == '1' for s in weld]
            left,bottom,right,top = weld
            #weldtime = match['weldtime']
            blockinfos[name]['collision'] = collision
            blockinfos[name]['attributes'] = attr
            blockinfos[name]['weldablesides'] = top,left,bottom,right

def getblockids() -> None:
    with openCfgPath("localGame.texture.blockIDFile") as f:
        data=smp.getsmpvalue(f.read())
    assert isinstance(data,dict)
    for name,i in data.items():
        assert isinstance(i,str)
        blockinfos[name]["id"] = int(i)
        idtoblock[int(i)] = name

def geticoncoords() -> None:
    with openCfgPath("localGame.texture.iconLocationFile") as f:
        data=smp.getsmpvalue(f.read())
    assert isinstance(data,dict)
    for icon,xy in data.items():
        assert isinstance(xy,str)
        x,y=xy.split(',')
        blockinfos[icon]["iconcoord"] = (int(x), int(y))

def substitutelocale(locale:str) -> str:
    # substitute locale entries into others
    # used in descriptions
    # a reference is {category name|mods}
    # mods is optional and is a string containing one or more of ^, s, or d
    lastob = 0 # the index to look for the next opening bracket at
    while '{' in locale[lastob:]:
        i_ob = locale.index('{',lastob)
        i_cb = locale.find('}', i_ob)
        if i_cb==-1: # there is no closing bracket
            break
        before=locale[:i_ob]
        middle=locale[i_ob+1:i_cb]
        after=locale[i_cb+1:]
        lastob=i_ob+1
        if '|' in middle:
            middle,modifier=middle.split('|',maxsplit=1)
        else:
            modifier=''
        key=tuple(part.strip() for part in middle.split())
        if key in globaLocale:
            localized=globaLocale[key]
            for mod in modifier:
                localized=modifiers[mod](localized)
            locale=before+localized+after
    return locale

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
                    globaLocale[tkey]=value

    for tkey,s in globaLocale.items():
        globaLocale[tkey]=substitutelocale(s)

def getentities() -> None:
    with openCfgPath("localGame.texture.entitiesFile") as f:
        data=smp.getsmpvalue(f.read())
    assert isinstance(data, dict)
    for name,entity in data.items():
        assert isinstance(entity, dict)
        texturePath = entity['texture']
        assert isinstance(texturePath, str)
        entities[name]={'texture':texturePath}

def assetinit() -> None:
    getblockids()
    getblockdefs()
    geticoncoords()
    getlocale()
    getentities()
