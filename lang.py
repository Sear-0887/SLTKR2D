import re
import collections
import os
import config

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
        with open(os.path.join(config.cmdlocaledir,fname)) as f:
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
                key=tuple(key.strip().split('.'))
                target=cmdi
                print(key)
                for k in key[:-1]:
                    target=target[k]
                target[key[-1]]=value
    #print(cmdi["help"]["aliases"])
    # EXCEPTIONS
    # nooo not the exceptions
    cmdi["link"]["desc"] = cmdi["link"]["desc"].format(linksstr) # aaaaaaaaaaaaaaaaaaaaaaaaaa
