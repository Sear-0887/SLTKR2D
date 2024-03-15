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
cmdi = {}
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
        
                    
# load the command locale
def phraser():
    loademoji()
    for langpth in glob.glob("lang/*"):
        lang = langpth[5:]
        try: cmdi[lang]
        except: cmdi[lang] = {}
        for i in glob.glob("lang/en/*.txt"):
            with open(i , "r") as f:
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
                    
                        
    print(cmdi['en']["help.aliases"])
    # EXCEPTIONS
    cmdi['en']["link.desc"] = cmdi['en']["link.desc"].format("".join([
    f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
    for name,data in keywords.items()
]))

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

def cfg(*args):
    target = config
    for key in args:
        target = target[key]
    return target

def loademoji():
    with open(cfg("infoPath","emojiInfoPath")) as f:
        global emojidict
        emojidict = json.load(f)
    return emojidict

def replacemoji(tar):
    if type(tar) != str: return tar
    for key, item in emojidict.items():
        tar = tar.replace(f":{key}:", item)
    return tar

def getdevs():
    with open(cfg("infoPath","devInfoPath")) as f:
        global devs
        devs = json.load(f)

def getkws(): 
    with open(cfg("infoPath","kwInfoPath")) as f:
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
