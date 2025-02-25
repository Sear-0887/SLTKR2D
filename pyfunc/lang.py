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
import collections
from typing import Any, TextIO, TypedDict

class Dev(TypedDict):
    name: str
    id: int
    github_link: str
    desc: str

cmdi: dict[str, dict[str, str | list[str]]] = {}
config = None
devs: list[Dev] = []
keywords: dict[str, dict[str, str]] = {}
presenseMsgs: dict[str, list] = {}
emojidict: dict[str, str] = {}

l = logging.getLogger()

# write_to_log, basically similar to print, with extra steps...
# ptnt is print_to_normal_terminal, ats is add_timestamp

# DEPRECATED - Use l.info()
# def lprint(*values: object, sep: str = " ",end: str = "\n", ptnt: bool = False, ats: bool = True) -> None:
#     valuesstr:str = sep.join(list(map(str, values))) + end
#     if ats:
#         valuesstr = time.strftime("%H:%M:%S", time.localtime()) + " | " + valuesstr
#     with open(f"cache/log/cache-{datetime.now():%d-%m-%Y}.txt", "a+", encoding="utf-8") as fil:
#         fil.write(valuesstr)
#     if ptnt:
#         print(valuesstr,end='')

cmdi = collections.defaultdict(dict)

def parseFile(filename: str, language: str) -> None:
    with open(os.path.join(cfgstr('locale.localePath'), language, filename), "r", encoding='utf-8') as f:
        linesIter = iter(f)
        for line in linesIter:
            # Replaces Backslash-newline to normal newline
            while line.endswith('\\\n'):
                line = line[:-2].strip() + '\n' + next(linesIter) # add the next line to this if this line ends with a backslash
            line = re.sub('#.*$','',line) # remove comments
            if '=' not in line: continue
            
            key, value = line.split('=',maxsplit=1)
            key = key.strip()
            value = replacEmojis(value.strip())
            valueFixed: str | list[str]
            if value.startswith('[') and value.endswith(']'): # List handling
                valueFixed = [v.strip() for v in value[1:-1].split(',') if len(v.strip()) > 0]
            else:
                valueFixed = value
            cmdi[language][key] = valueFixed

# load the command locale
def parseLangFiles() -> None:
    loadEmoji()
    for language in os.listdir(cfgstr('locale.localePath')):
        for filePath in os.listdir(os.path.join(cfgstr('locale.localePath'), language)):
            parseFile(filePath, language)

        # EXCEPTIONS
        linkDesc = cmdi[language]["link.desc"]
        assert isinstance(linkDesc, str)
        cmdi[language]["link.desc"] = linkDesc.format("".join([
            f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
            for name,data in keywords.items()
        ]))

# Unused
def doesModuleLangExist(module:str) -> bool: # reloads the locale from one file in each locale folder
    found=False # did it find any locale files?
    for langPath in glob.glob("lang/*"):
        lang = langPath[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        try:
            parseFile(os.path.join('lang', lang, module + '.txt'), lang)
            found=True
        except FileNotFoundError:
            l.warning(f"Locale for {module} in {lang} wasn't found")
    return found

# get a locale entry
def evl(*args: str, lang: str = "en") -> str | list:
    target = ".".join(args)
    try:
        return cmdi[lang][target]
    except:
        return ""

def handleHostID() -> tuple[int, list[bool]]:
    raw = getclientenv('HOSTID') or  "CLIENT--0"
    match = re.fullmatch(r"^CLIENT\-(\w*)\-(.*)", raw)
    if match is not None:
        auid, setting = match.groups()
    else:
        auid, setting = '', '0'
    if not auid: auid = "0"
    returnTuple = ( int(auid, 16), list(map(lambda x:x=="1", list(setting))) )
    return returnTuple

def loadConfig() -> None:
    with open("config.json", encoding="utf-8") as f:
        global config
        config = json.load(f)
        hostid, settings = handleHostID()
        config['ShowHost'] = settings[0]
        config['HostDCID'] = hostid
        config['PREFIX'] = getclientenv('PREFIX') or "!"

def cfgstr(target:str) -> str:
    if config is None: loadConfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base,str)
    return base

def openCfgPath(target: str, mode:str = 'r', encoding:str|None = "utf-8", **kwargs: Any) -> TextIO:
    path = cfgstr(target)
    fileObj: TextIO = open(path, mode, encoding=encoding, **kwargs)
    return fileObj

def cfg(target:str) -> int | str | list | dict:
    if config is None: loadConfig()
    base = config
    for tv in target.split("."):
        assert isinstance(base,dict)
        base = base[tv]
    assert isinstance(base, (int, str, list, dict))
    return base

def loadEmoji() -> None:
    with openCfgPath("infoPath.emojiInfoPath") as f:
        global emojidict
        emojidict = json.load(f)

def replacEmojis(tar:str) -> str:
    if type(tar) != str: return tar
    for key, item in emojidict.items():
        tar = tar.replace(f":{key}:", item)
    return tar

def getDevs() -> None:
    with openCfgPath("infoPath.devInfoPath") as f:
        global devs
        devs = json.load(f)
        
def getPresenseMsgs() -> None:
    with openCfgPath("infoPath.presenseInfoPath") as f:
        global presenseMsgs
        presenseMsgs = json.load(f)

def getKeywords() -> None: 
    with openCfgPath("infoPath.kwInfoPath") as f:
        global keywords
        keywords = json.load(f)

def getArrowCoords() -> dict[str, tuple[int, int]]:
    racord:dict[str, tuple[int, int]] = {}
    with openCfgPath("localGame.texture.guidebookArrowCordFile") as f:
        data=getsmpvalue(f.read())
    assert isinstance(data,dict)
    for icon,xy in data.items():
        assert isinstance(xy,str)
        x,y=xy.split(',')
        racord[icon] = (int(x), int(y))
    return racord

def botinit() -> None:
    from pyfunc.assetload import assetinit
    loadConfig()
    getKeywords()
    parseLangFiles() # command locale
    getPresenseMsgs()
    getDevs()
    assetinit() # roody locale and blocks
