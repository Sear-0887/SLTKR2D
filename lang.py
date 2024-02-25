import glob
import re
import collections

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

# delete 
# def repri(): # USED FOR MIGRATING FROM CLASS METHOD TO .TXT FILES
#     for cmdname in dir(cmds): 
#         if not cmdname.startswith('__'):
#             clas = getattr(cmds, cmdname)
#             for cmdattr in dir(clas):
#                 if not cmdattr.startswith('__'):
#                     print(f"{cmdname}.{cmdattr} = {getattr(clas, cmdattr)}")
#             print("\n")

# ???

def phraser():
    for fname in os.listdir(config.cmdlocaledir):
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
    target = target.split(".") # why this when cmdi always has two levels
    root = cmdi
    for i in target:
        root = root[i]
    return root
