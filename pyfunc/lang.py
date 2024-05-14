# the links
# key is link name
# value['link'] is the url
# value['kw'] is the keywords !link recognizes

# the links as one string (used to format into !link description)

import logging
import time
import os
from pyfunc.gettoken import getclientenv
from pyfunc.smp import getsmpvalue
import json
from datetime import datetime
import glob
import re
from dotenv import dotenv_values
import collections
from typing import Any, TextIO, TypedDict

class Dev(TypedDict):
    name:str
    id:int
    github_link:str
    desc:str

cmdi:dict[str, dict[str, str | list[str]]] = {}
config = None
devs:list[Dev] = []
keywords:dict[str, dict[str, str]] = {}
l = logging.getLogger()
presensemsg:dict[str, list] = {}
emojidict:dict[str, str] = {}

# write_to_log, basically similar to print, with extra steps...
# ptnt is print_to_normal_terminal, ats is add_timestamp
def lprint(*values: object, sep: str = " ",end: str = "\n", ptnt: bool = False, ats: bool = True) -> None:
    valuesstr:str = sep.join(list(map(str, values))) + end
    if ats:
        valuesstr = time.strftime("%H:%M:%S", time.localtime()) + " | " + valuesstr
    with open(f"cache/log/cache-{datetime.now():%d-%m-%Y}.txt", "a+", encoding="utf-8") as fil:
        fil.write(valuesstr)
    if ptnt:
        print(valuesstr,end='')

cmdi = collections.defaultdict(dict)

def phraserfile(fname:str,lang:str) -> None:
    with open(os.path.join(cfgstr('locale.localePath'),lang,fname), "r", encoding='utf-8') as f:
        linesiter=iter(f)
        for line in linesiter:
            while line.endswith('\\\n'):
                line=line[:-2].strip()+'\n'+next(linesiter) # add the next line to this if this line ends with a backslash
            line=re.sub('#.*$','',line) # remove comments
            if '=' not in line:
                continue
            key,value=line.split('=',maxsplit=1)
            value=replacemoji(value.strip())
            value2:str | list[str]
            if value.startswith('[') and value.endswith(']'):
                value2=[v.strip() for v in value[1:-1].split(',') if len(v.strip())>0]
            else:
                value2 = value
            key=key.strip()
            cmdi[lang][key]=value2

# load the command locale
def phraser() -> None:
    loademoji()
    for lang in os.listdir(cfgstr('locale.localePath')):
        for i in os.listdir(os.path.join(cfgstr('locale.localePath'),lang)):
            phraserfile(i,lang)
        l.debug(cmdi[lang]["help.aliases"])
        # EXCEPTIONS
        linkdesc = cmdi[lang]["link.desc"]
        assert isinstance(linkdesc, str)
        cmdi[lang]["link.desc"] = linkdesc.format("".join([
            f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
            for name,data in keywords.items()
        ]))

def phrasermodule(module:str) -> bool: # reloads the locale from one file in each locale folder
    found=False # did it find any locale files?
    for langpth in glob.glob("lang/*"):
        lang = langpth[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        try:
            phraserfile(os.path.join('lang',lang,module+'.txt'),lang)
            found=True
        except FileNotFoundError:
            l.warning(f"locale for {module} in {lang} wasn't found")
    return found

# get a locale entry
def evl(*args:str, lang:str="en") -> str | list:
    target = ".".join(args)
    try:
        return cmdi[lang][target]
    except:
        return ""

def handlehostid() -> tuple[int, list[bool]]:
    raw = getclientenv('HOSTID') or  "CLIENT--0"
    match = re.fullmatch(r"^CLIENT\-(\w*)\-(.*)", raw)
    if match is not None:
        auid, setting = match.groups()
    else:
        auid, setting = '', '0'
    if not auid: auid = "0"
    returntup = ( int(auid, 16), list(map(lambda x:x=="1", list(setting))) )
    return returntup

def loadconfig() -> None:
    with open("config.json", encoding="utf-8") as f:
        global config
        config = json.load(f)
        hostid, settings = handlehostid()
        config['ShowHost'] = settings[0]
        config['HostDCID'] = hostid
        config['PREFIX'] = getclientenv('PREFIX') or "!"

def cfgstr(target:str) -> str:
    if config is None: loadconfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base,str)
    return base

def opencfg(target:str, *args:Any, **kwargs:Any) -> TextIO:
    return open(cfgstr(target), *args, **kwargs)

def cfg(target:str) -> int | str | list | dict:
    if config is None: loadconfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base, (int, str, list, dict))
    return base

def loademoji() -> None:
    with opencfg("infoPath.emojiInfoPath", encoding="utf-8") as f:
        global emojidict
        emojidict = json.load(f)

def replacemoji(tar:str) -> str:
    if type(tar) != str: return tar
    for key, item in emojidict.items():
        tar = tar.replace(f":{key}:", item)
    return tar

def getdevs() -> None:
    with opencfg("infoPath.devInfoPath", encoding="utf-8") as f:
        global devs
        devs = json.load(f)
        
def getpresense() -> None:
    with opencfg("infoPath.presenseInfoPath", encoding="utf-8") as f:
        global presensemsg
        presensemsg = json.load(f)

def getkws() -> None: 
    with opencfg("infoPath.kwInfoPath", encoding="utf-8") as f:
        global keywords
        keywords = json.load(f)

def getarrowcoords() -> dict[str, tuple[int, int]]:
    racord:dict[str, tuple[int, int]] = {}
    with opencfg("localGame.texture.guidebookArrowCordFile", encoding="utf-8") as f:
        data=getsmpvalue(f.read())
    assert isinstance(data,dict)
    for icon,xy in data.items():
        assert isinstance(xy,str)
        x,y=xy.split(',')
        racord[icon] = (int(x), int(y))
    return racord

def botinit() -> None:
    from pyfunc.assetload import assetinit
    os.makedirs(cfgstr('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfgstr('logFolder'), exist_ok=True) # logs folder (may be in cache)
    loadconfig()
    getkws()
    phraser() # command locale
    getpresense()
    getdevs()
    assetinit() # roody locale and blocks
