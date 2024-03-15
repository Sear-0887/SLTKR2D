# the links
# key is link name
# value['link'] is the url
# value['kw'] is the keywords !link recognizes


# the links as one string (used to format into !link description)



import time
import os

import json
from datetime import datetime
import glob
import re
from dotenv import dotenv_values
import collections
config = None
devs = None
keywords = {}

# write_to_log, basically similar to print, with extra steps...
# ptnt is print_to_normal_terminal, ats is add_timestamp
def lprint(*values: object, sep: str | None = " ",end: str | None = "\n", ptnt: bool = False, ats: bool = True) -> None:
    with open(f"cache/log/cache-{datetime.now():%d-%m-%Y}.txt", "a+") as fil:
        values = sep.join(list(map(str, values))) + end
        if ats:
            values = time.strftime("%H:%M:%S", time.localtime()) + " | " + values
        fil.write(values)
    if ptnt:
        print(values,end='')

def recursiveddict():
    return collections.defaultdict(recursiveddict)

cmdi = recursiveddict()

def phraser():
    for lang in os.listdir(cfg('local.localPath')):
        for fname in os.listdir(os.path.join(cfg('local.localPath'),lang)): # you could filter for only .txt files
            with open(os.path.join(cfg('local.localPath'),lang,fname)) as f:
                linesiter=iter(f)
                for line in linesiter:
                    while line.endswith('\\\n'):
                        line=line[:-2].strip()+'\n'+next(linesiter) # add the next line to this if this line ends with a backslash
                    line=re.sub('#.*$','',line) # remove comments
                    if '=' not in line:
                        continue
                    key,value=line.split('=',maxsplit=1)
                    value=value.strip()
                    if value.startswith('[') and value.endswith(']'):
                        value=[v.strip() for v in value[1:-1].split(',') if len(v.strip())>0]
                    key=key.strip()
                    cmdi[lang][key]=value
        print(lang,cmdi[lang]["help.aliases"])
    # EXCEPTIONS
    # nooo not the exceptions
    for lang in cmdi:
        cmdi[lang]["link.desc"] = cmdi[lang]["link.desc"].format("".join([
            f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
            for name,data in keywords.items()
        ])) # aaaaaaaaaaaaaaaaaaaaaaaaaa

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
    with open("config.json") as f:
        global config
        config = json.load(f)
        hostid, settings = handlehostid()
        config['ShowHost'] = settings[0]
        config['HostDCID'] = hostid
    return config

def cfg(*target):
    if config is None: loadconfig()
    base = config
    target = ".".join(target)
    for tv in target.split("."):
        base = base[tv]
    return base

def loademoji():
    with open(cfg("infoPath.emojiInfoPath")) as f:
        global emojidict
        emojidict = json.load(f)
    return emojidict

def replacemoji(tar):
    if type(tar) != str: return tar
    for key, item in emojidict.items():
        tar = tar.replace(f":{key}:", item)
    return tar

def getdevs():
    with open(cfg("infoPath.devInfoPath")) as f:
        global devs
        devs = json.load(f)

def getkws(): 
    with open(cfg("infoPath.kwInfoPath")) as f:
        global keywords
        keywords = json.load(f)
    return keywords
        
def botinit():
    from pyfunc.assetload import assetinit
    os.makedirs(cfg('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfg('logFolder'), exist_ok=True) # logs folder (may be in cache)
    loadconfig()
    getkws()
    phraser() # command locale
    getdevs()
    assetinit() # roody locale and blocks
    loademoji()