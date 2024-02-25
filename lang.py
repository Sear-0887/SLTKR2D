import re
import collections
import os

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

def recursiveddict():
    return collections.defaultdict(recursiveddict)

cmdi = recursiveddict()

def phraser():
    for fname in os.listdir(config.cmdlocaledir): # you could filter for only .txt files
        with open(fname) as f:
            linesiter=iter(f)
            for line in linesiter:
                while line.endswith('\\\n'):
                    line=line[:-2].strip()+'\n'+next(linesiter) # add the next line to this if this line ends with a backslash
                line=re.sub('#.*$','',line) # remove comments
                if '=' not in line:
                    continue
                key,value=line.split('=',maxsplit=1)
                key=tuple(key.split('.'))
                target=cmdi
                for k in key[:-1]:
                    target=target[k]
                target[k[-1]]=value.strip()
    #print(cmdi["help"]["aliases"])
    # EXCEPTIONS
    cmdi["link"]["desc"] = cmdi["link"]["desc"].format(linksstr) # aaaaaaaaaaaaaaaaaaaaaaaaaa

def evl(target):
    target = target.split(".")
    out = cmdi
    for i in target:
        out = out[i]
    return out
