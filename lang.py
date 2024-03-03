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

# write_to_log, basically similar to print, with extra steps...
# ptnt is print_to_normal_terminal, ats is add_timestamp
def lprint(*values: object, sep: str | None = " ",end: str | None = "\n", ptnt: bool = False, ats: bool = True) -> None:
    with open(f"cache/log/cache-{datetime.now():%d-%m-%Y}.txt", "a") as fil:
        values = sep.join(values) + end
        if ats:
            values = time.strftime("%H:%M:%S", time.localtime()) + " | " + values
        fil.write(values)
    if ptnt:
        print(values)

def recursiveddict():
    return collections.defaultdict(recursiveddict)

cmdi = recursiveddict()

def phraser():
    for lang in os.listdir(config.cmdlocaledir): # you could filter for only .txt files
        for fname in os.listdir(os.path.join(config.cmdlocaledir,lang)): # you could filter for only .txt files
            with open(os.path.join(config.cmdlocaledir,lang,fname)) as f:
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
                    target=cmdi[lang]
                    print(key)
                    for k in key[:-1]:
                        target=target[k]
                    target[key[-1]]=value
    #print(cmdi["help"]["aliases"])
    # EXCEPTIONS
    # nooo not the exceptions
    for lang in cmdi:
        cmdi[lang]["link"]["desc"] = cmdi[lang]["link"]["desc"].format(linksstr) # aaaaaaaaaaaaaaaaaaaaaaaaaa

    cmdi=cmdi['en'] # temporary