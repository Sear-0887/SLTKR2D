# the links
# key is link name
# value['link'] is the url
# value['kw'] is the keywords !link recognizes

# the links as one string (used to format into !link description)

import logging
import time
import os
from pyfunc.smp import getsmpvalue
import json
from datetime import datetime
import glob
import re
from dotenv import dotenv_values
import collections

cmdi:dict[str, dict[str, str]] = {}
config = {}
devs = {}
keywords:dict[str, dict[str, str]] = {}
l = logging.getLogger()

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

def phraserfile(fname,lang):
    with open(os.path.join(cfg('locale.localePath'),lang,fname), "r", encoding='utf-8') as f:
        linesiter=iter(f)
        for line in linesiter:
            while line.endswith('\\\n'):
                line=line[:-2].strip()+'\n'+next(linesiter) # add the next line to this if this line ends with a backslash
            line=re.sub('#.*$','',line) # remove comments
            if '=' not in line:
                continue
            key,value=line.split('=',maxsplit=1)
            value=replacemoji(value.strip())
            if value.startswith('[') and value.endswith(']'):
                value=[v.strip() for v in value[1:-1].split(',') if len(v.strip())>0]
            key=key.strip()
            cmdi[lang][key]=value

# load the command locale
def phraser() -> None:
    loademoji()
    for lang in os.listdir(cfg('locale.localePath')):
        for i in os.listdir(os.path.join(cfg('locale.localePath'),lang)):
            phraserfile(i,lang)
        l.debug(cmdi[lang]["help.aliases"])
        # EXCEPTIONS
        cmdi[lang]["link.desc"] = cmdi[lang]["link.desc"].format("".join([
            f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
            for name,data in keywords.items()
        ]))

def phrasermodule(module:str): # reloads the locale from one file in each locale folder
    found=False # did it find any locale files?
    for langpth in glob.glob("lang/*"):
        lang = langpth[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        try:
            phraserfile(os.path.join('lang',lang,module+'.txt'),lang)
            found=True
        except FileNotFoundError:
            l.info(f"WARNING: locale for {module} in {lang} wasn't found")
    return found

# get a locale entry
def evl(*args, lang="en") -> str | list:
    target = ".".join(args)
    try:
        return cmdi[lang][target]
    except:
        return ""

def handlehostid() -> tuple[int, list[bool]]:
    raw = ""
    try:
        raw2 = dotenv_values("cred/client.env")['HOSTID']
        if raw2 is None:
            raise Exception("No HOSTID.")
        raw = raw2
    except Exception as e:
        l.warning(f"ReadingHostID Failed {e}")
        raw = "CLIENT--0"
    match = re.fullmatch(r"^CLIENT\-(\w*)\-(.*)", raw)
    if match is not None:
        auid, setting = match.groups()
    else:
        auid, setting = '', '0'
    if not auid: auid = "0"
    returntup = ( int(auid, 16), list(map(lambda x:x=="1", list(setting))) )
    return returntup

def loadconfig():
    with open("config.json", encoding="utf-8") as f:
        global config
        config = json.load(f)
        hostid, settings = handlehostid()
        config['ShowHost'] = settings[0]
        config['HostDCID'] = hostid
        config['PREFIX'] = dotenv_values("cred/client.env")['PREFIX']
    return config

def cfg(*target):
    if config is None: loadconfig()
    base = config
    target = ".".join(target)
    for tv in target.split("."):
        base = base[tv]
    return base

def loademoji():
    with open(cfg("infoPath.emojiInfoPath"), encoding="utf-8") as f:
        global emojidict
        emojidict = json.load(f)
    return emojidict

def replacemoji(tar):
    if type(tar) != str: return tar
    for key, item in emojidict.items():
        tar = tar.replace(f":{key}:", item)
    return tar

def getdevs():
    with open(cfg("infoPath.devInfoPath"), encoding="utf-8") as f:
        global devs
        devs = json.load(f)
        
def getpresense():
    with open(cfg("infoPath.presenseInfoPath"), encoding="utf-8") as f:
        global presensemsg
        presensemsg = json.load(f)
    return presensemsg

def getkws(): 
    with open(cfg("infoPath.kwInfoPath"), encoding="utf-8") as f:
        global keywords
        keywords = json.load(f)
    return keywords

def getarrowcoords():
    racord = {}
    with open(cfg("localGame.texture.guidebookArrowCordFile"), encoding="utf-8") as f:
        data=getsmpvalue(f.read())
    for icon,xy in data.items():
        x,y=xy.split(',')
        racord[icon] = (int(x), int(y))
    return racord

def botinit():
    
    from pyfunc.assetload import assetinit
    os.makedirs(cfg('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfg('logFolder'), exist_ok=True) # logs folder (may be in cache)
    loadconfig()
    global keywords
    keywords = getkws()
    phraser() # command locale
    getpresense()
    getdevs()
    assetinit() # roody locale and blocks
