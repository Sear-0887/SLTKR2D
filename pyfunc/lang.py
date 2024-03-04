keywords = {
    "Roody:2D Game Discord Server": {
        "link": "https://discord.gg/gbEkBNt",
        "kw": ["r2d", "roody2d", "roody:2d", "game", "gameser", "gamedc"]
    },
    "SLTK Wiki Server": {
        "link": "https://discord.gg/cDAUYrtjzV",
        "kw": ["sltk", "wikiser", "wikidc", "r2dwiki", "r2dwikiser"]
    },
    "SLTK Wiki Page": {
        "link": "https://roody2d.wiki.gg",
        "kw": ["wiki", "sltkwiki", "wikipage", "r2dwiki"]
    }
}

linksstr="".join([
    f"{name} ({data['link']})\nKeywords: `{'`, `'.join(data['kw'])}`\n"
    for name,data in keywords.items()
])


import time
import json
from datetime import datetime
import glob
import re
cmdi = {}
# config:dict = {}

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
        
                    
def phraser():
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
                        cmdi[lang][expr] = val
                        lprint(f"{(expr, val) =}")
                    
                        
    print(cmdi['en']["help.aliases"])
    # EXCEPTIONS
    cmdi['en']["link.desc"] = cmdi['en']["link.desc"].format(linksstr)

def evl(target, lang="en") -> str | list:
    try:
        return cmdi[lang][target]
    except:
        return ""

def loadconfig():
    with open("config.json") as f:
        global config
        config = json.load(f)
    return config

def cfg(target):
    base = config
    for tv in target.split("."):
        base = base[tv]
    return base