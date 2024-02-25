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



import glob
import re
cmdi = {}

# def repri(): # USED FOR MIGRATING FROM CLASS METHOD TO .TXT FILES
#     for cmdname in dir(cmds): 
#         if not cmdname.startswith('__'):
#             clas = getattr(cmds, cmdname)
#             for cmdattr in dir(clas):
#                 if not cmdattr.startswith('__'):
#                     print(f"{cmdname}.{cmdattr} = {getattr(clas, cmdattr)}")
#             print("\n")
                    
def phraser():
    for i in glob.glob("lang/en/*.txt"):
        with open(i , "r") as f:
            fc = re.sub(r"\\\s*\n", r"\\", f.read())
            for line in fc.split("\n"):
                if line.startswith("##"): continue
                for cmd, ele, val in re.findall(r"^(\w+).(\w+)\s*=\s*(.+)", line):
                    val = val.replace("\\", "\n")
                    if re.match(r"^\[.*\]$", val):
                        val = val[1:-1].split(", ")
                        if val == ['']: val = []
                    try: cmdi[cmd]
                    except: cmdi[cmd] = {}
                    cmdi[cmd][ele] = val
    print(cmdi["help"]["aliases"])
    # EXCEPTIONS
    cmdi["link"]["desc"] = cmdi["link"]["desc"].format(linksstr)

def evl(target):
    target = target.split(".")
    root = cmdi
    for i in target:
        root = root[i]
    return root
