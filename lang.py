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
    for i in glob.glob("lang/en/*.txt"): # for each file in lang/en (use os.listdir)
        with open(i , "r") as f: # open the file
            fc = re.sub(r"\\\s*\n", r"\\", f.read()) # w h y
            for line in fc.split("\n"): # read each line
                if line.startswith("##"): continue # skip comments
                for cmd, ele, val in re.findall(r"^(\w+)\.(\w+)\s*=\s*(.+)", line): # dot needs to be escaped # get word.word=text
                    val = val.replace("\\", "\n") # undo the w h y
                    if re.match(r"^\[.*\]$", val): # if val is bracketed: 
                        val = val[1:-1].split(", ") # convert it to a list
                        if val == ['']: val = [] # without empty elements
                    try: cmdi[cmd] # use collections.defaultdict
                    except: cmdi[cmd] = {} # seriously
                    cmdi[cmd][ele] = val
    print(cmdi["help"]["aliases"])
    # EXCEPTIONS
    cmdi["link"]["desc"] = cmdi["link"]["desc"].format(linksstr) # aaaaaaaaaaaaaaaaaaaaaaaaaa

def evl(target):
    target = target.split(".") # why this when cmdi always has two levels
    root = cmdi
    for i in target:
        root = root[i]
    return root
