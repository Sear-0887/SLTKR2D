# the links
# key is link name
# value['link'] is the url
# value['kw'] is the keywords !link recognizes

# the links as one string (used to format into !link description)

import time
import os
from pyfunc.smp import getsmpvalue
import json
from datetime import datetime
import glob
import re
from dotenv import dotenv_values
cmdi = {}
config = None
devs = None
keywords = {}

# write_to_log, basically similar to print, with extra steps...
# ptnt is print_to_normal_terminal, ats is add_timestamp
def lprint(*values: object, sep: str | None = " ",end: str | None = "\n", ptnt: bool = False, ats: bool = True) -> None:
    with open(f"cache/log/cache-{datetime.now():%d-%m-%Y}.txt", "a+", encoding="utf-8") as fil:
        values = sep.join(list(map(str, values))) + end
        if ats:
            values = time.strftime("%H:%M:%S", time.localtime()) + " | " + values
        fil.write(values)
    if ptnt:
        print(values,end='')

def phraserfile(fname,lang):
    with open(fname , "r", encoding='utf-8') as f:
        fc = re.sub(r"\\\s*\n", r"\\", f.read())
        for line in fc.split("\n"):
            if line.startswith("##"): continue
            for expr, val in re.findall(r"^([\w.]+)\s*=\s*(.+)", line):
                val = val.replace("\\", "\n")
                if re.match(r"^\[.*\]$", val):
                    val = val[1:-1].split(", ")
                    if val == ['']: val = []
                val = replacemoji(val)
                cmdi[lang][expr] = val
                lprint(f"{(expr, val) =}")

# load the command locale
def phraser():
    loademoji()
    for langpth in glob.glob("lang/*"):
        lang = langpth[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        for i in glob.glob("lang/en/*.txt"):
            phraserfile(i,lang)
    print(cmdi['en']["help.aliases"])
    # EXCEPTIONS
    cmdi['en']["link.desc"] = cmdi['en']["link.desc"].format("".join([
        f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
        for name,data in keywords.items()
    ]))

def phrasermodule(module): # reloads the locale from one file in each locale folder
    found=False # did it find any locale files?
    for langpth in glob.glob("lang/*"):
        lang = langpth[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        try:
            phraserfile(os.path.join('lang',lang,module+'.txt'),lang)
            found=True
        except FileNotFoundError:
            lprint(f"WARNING: locale for {module} in {lang} wasn't found")
    return found

# get a locale entry
def evl(*args, lang="en") -> str | list:
    target = ".".join(args)
    try:
        return cmdi[lang][target]
    except:
        return ""

def handlehostid():
    raw = ""
    try:
        raw = dotenv_values("cred/client.env")['HOSTID']
    except Exception as e:
        print(f"ReadingHostID Failed {e}")
        raw = "CLIENT--0"
    auid, setting = re.fullmatch(r"^CLIENT\-(\w*)\-(.*)", raw).groups()
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
    getdevs()
    assetinit() # roody locale and blocks