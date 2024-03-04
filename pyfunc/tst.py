import re
from PIL import Image
from pyfunc.lang import cmd, keywords
import pyfunc.block_extra as be

quickidtable = ["NIC"]*102
blockinfos = {}
def getblockid():
    with open("block_id_.smp") as f:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{([\d]*)\}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["id"] = int(i)
            quickidtable[int(i)] = n
def getblockpath():
    with open("block_textures.smp") as f:
        pattern = re.compile(r"{(.*)}:{(.*)}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["path"] = i         

def getblockcord():
    with open("block_icons.smp") as gbc:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{\s*([\d]*),\s*([\d]*)\}")
        for a, x, y in re.findall(pattern, gbc.read()):
            blockinfos[a]["iconcord"] = (int(x), int(y))
    return False

def frs(east, south, west, north, wt, flg):
    wt = int(wt, 2)
    info = int(east)*8+int(south)*4+int(west)*2+int(north)
    print(info, east, south, west, north, flg, wt)
    info = info & wt & flg 
    print(str(bin(info))[2:].zfill(4))
    info = list(str(bin(info))[2:].zfill(4))
    print(flg, info)
    east = int(east and info[0])*16
    south = int(south and info[1])*16
    west = int(west and info[2])*16
    north = int(north and info[3])*16
    return ((west  , north  , west+8  , north+8  ),
            (east+8, north  , east+8+8, north+8  ),
            (west  , south+8, west+8  , south+8+8),
            (east+8, south+8, east+8+8, south+8+8))


def image(dt="[[16][20]][[16][16]]"):
    blockp = []#3layer
    cordic = []
    cordwr = []
    width, height = 0, 0 
    dt.replace(" ", "")
    dt = dt.lower()
    for y, row in enumerate(re.findall(r"\[(\[.*?\])\]+", dt)):
        for x, raw in enumerate(re.findall(r"\[([\w]+)#?([\d]{4}|)#?([\d]{1}|)\]", row)):
            block, weldtag, rotation = raw
            if not weldtag: weldtag = "1111"
            if block.isdigit():
                block = quickidtable[int(block)]
                print(block, weldtag, rotation, x, y)
            if block != "NIC" and block != "air":
                if block in be.wiredtypes:
                    if block in be.wafertypes:
                        blockp += [("wafer", weldtag, x, y),
                                    (block, "0000", x, y)]
                        blockp += [("wire", weldtag, x, y)]
                    if block in be.frametypes:
                        blockp += [("frame", weldtag, x, y), 
                                    (block, "0000", x, y)]
                        blockp += [("wire", weldtag, x, y)]
                    if block == "actuator":
                        blockp += [("actuator_base", "0001", x, y), 
                                ("actuator_head", "1111", x, y)]
                    cordwr += [(x,y)]
                    
                else:
                    blockp += [(block, weldtag, x, y)]
                    print("T")
            cordic += [(x, y)]
        width = max(width, x+1)
    height = max(height, y+1)
    print("WIDTH, HEIGHT =", width, height)
    fin = Image.new("RGBA", (width*16, height*16))
    print(blockp)
    for name, wt, x, y in blockp:#     e1,0   s0,1   w-1,0  n 0,-1 
        print("")
        print("name,wt,(x,y)", name, wt, (x, y))
        print("BLOCKPATH = textures/blocks/"+blockinfos[name]["path"])
        src = Image.open("textures/blocks/"+blockinfos[name]["path"]).convert("RGBA")
        spflg = "1111"
        findcord = cordwr if name == "wire" else cordic
        for i, j in be.weldspr.items():
            if name in j: 
                spflg = i
        
        cord = frs(
            (x+1, y) in findcord, 
            (x, y+1) in findcord, 
            (x-1, y) in findcord, 
            (x, y-1) in findcord, 
            wt,
            int(spflg, 2))
        print(cord, spflg)
        for e, crd in enumerate(cord):
            fin.alpha_composite(src.crop(crd), (x*16+(e%2)*8, y*16+(e//2)*8))
    fin = fin.resize((width*16*2, height*16*2), Image.NEAREST)
    fin.save("f.png")

getblockid()
getblockpath()
getblockcord()
image("[[wire][actuator]]")