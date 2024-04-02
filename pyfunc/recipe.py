import PIL.Image
import collections
import glob
from PIL import Image
import os
import pyfunc.gif as gif
# import gif
from typing import Any
from pyfunc.lang import botinit, cfg, getarrowcoords
from pyfunc.smp import getsmpvalue
from pyfunc.block import canweld, get, makeimage, rotatewelded
from pyfunc.assetload import blockinfos


botinit()

def cropempty(img: PIL.Image):
    return img.crop(img.getbbox())

def sumtuple(*tuples):
    return tuple(map(sum, zip(*tuples)))

def massstrip(l:list):
    for i, j in enumerate(l):
        l[i] = j.strip()
    return l

def handletags(s:Any, organdict:dict) -> str | list:
    if not isinstance(s, str): return s 
    if s.startswith('$'):
        if s[1:] in organdict['tag'].keys():
            return organdict['tag'][s[1:]]
        print('Just a Normal name starts with $ ???????')
    return s

def handlegridtags(s:list, organdict:dict) -> tuple[list, str]:
    for y, xaxis in enumerate(s):
        for x, critem in enumerate(xaxis):
            s[y][x] = handletags(critem, organdict)
    return s

def getarrowimg(name):
    icox, icoy = getarrowcoords()[name]
    return Image.open(
        cfg("localGame.texture.guidebookArrowFile")).crop(
            (16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))
        ).resize((64, 64), Image.NEAREST
    )

def addentries(i, entryname:str, typ:str, organdict:dict, includestr:str) -> list:
    includes = massstrip(includestr.split(','))
    entries = collections.defaultdict(None)
    for key, item in i.items():
        item = handletags(item, organdict)
        if isinstance(item, str) and item.isdigit(): # Handle Numbers Differently
            item = int(item)
        if typ == 'heat' and key == 'needs_entity': # True for needs_entity
            item = bool(item)
        if typ == 'combine' and key == 'grid': # Handles combine grid properties
            item = handlegridtags(item, organdict)
        i[key] = item
        if key in includes:
            entries[key] = i[key]
    if entryname not in organdict[typ].keys():
        organdict[typ][entryname] = []
    organdict[typ][entryname].append(entries)
    
def testing():
    with open("gameAssets/recipes.smp") as f:
        organdict = collections.defaultdict(dict)
        rawdata = getsmpvalue(f.read())
        for i in rawdata:
            producename = ""
            col = ""
            if i['type'] == 'tag': # Tags
                organdict['tag'][i['name']] = i['blocks']
                continue
            elif i['type'] == 'heat': # Heating Recipe
                producename = i['product']
                col = 'ingredient, time, surrounding, needs_entity'
            elif i['type'] == 'extract': # Extracting Recipe
                producename = i['product']
                col = 'ingredient, time, amount, post_action'
            elif i['type'] == 'inject': # Injecting Recipe
                if 'transform_receiver' in i['product'].keys(): # Normal Injection
                    producename = i['product']['transform_receiver']
                elif 'fertilizer' in i['product'].keys(): # Fertilizing Injection
                    producename = i['receiver']
                col = 'pill, receiver, needs_passive'
            elif i['type'] == 'combine': # Combining Recipe
                i['amount'] = i['product']['amount']
                i['block'] = i['product']['block']
                producename = i['block']
                col = 'amount, grid, block'
            addentries(
                i, 
                producename, 
                i['type'], 
                organdict, 
                col)
            ...
    return organdict
returned = testing()


# Massive Comments Below to perform the Rubber duck debugging (https://en.wikipedia.org/wiki/Rubber_duck_debugging)
def generates(generated, recipenum=0, prodname="unknown", replacedhistroy="", pthname=None, ratio=4):
    pthname = pthname or f"cache/recipeframe-{prodname}-{recipenum}{replacedhistroy}.png"
    print(f"Generating | {pthname}") # Debug Purpose, Not removing in case
    for y, yaxis in enumerate(generated): # Open Grid
        for x, critem in enumerate(yaxis): # Scan through each block
            if critem == "NIC": critem = "air" # Convert NIC to air
            if isinstance(critem, list): # If it's a list, it's a tag, which
                place = critem # Store the original list for the next iter to process
                for i in critem: # loops through tags element
                    generated[y][x] = {"type":i,"rotate":0,"weld":[True]*4,"data":None} # Modify the list element to be the block
                    generates(generated, recipenum, prodname, f"{replacedhistroy}~{i}") # Recursive, Passes the copy and informations to the sub process
                generated[y][x] = place # Places back the original list for the next iter to process
                return # Terminates the attempt as it is useless
            elif isinstance(critem, str): # It's normal and needed to be NORMALIZE
                generated[y][x] = {"type":critem,"rotate":0,"weld":[True]*4,"data":None} # Actions
    else: 
        for y, yaxis in enumerate(generated): # Open Grid
            for x, critem in enumerate(yaxis): # Scan through each block
                print(get(generated, x, y))
                copy = critem
                for i in range(4):
                    if (
                        canweld('right',copy) and canweld('left',get(generated,x+1,y)) or
                        canweld('left',copy) and canweld('right',get(generated,x-1,y)) or
                        canweld('bottom',copy) and canweld('top',get(generated,x,y+1)) or
                        canweld('top',copy) and canweld('bottom',get(generated,x,y-1))
                        ):
                        print(f"found")
                        copy = critem
                        generated[y][x] = copy
                        break
                    else:
                        print("No possible welding found, rotates")
                        copy['rotate'] += 1
                        copy['rotate'] %= 4
                        copy['weld'] = rotatewelded(copy['weld'], copy['rotate'])
                
        ... 
        gen = makeimage(generated) # Make Image
        width, height = gen.size # Get width, height
        gen = gen.resize((width*ratio, height*ratio), Image.NEAREST).convert("RGBA") # Resize to dimension*Ratio
        gen.save(pthname) # Save the final image

def generaterecipe(name, apng=False):
    if name not in blockinfos.keys(): raise KeyError({'block':name})
    finimage = gif.gif((50, 50, 50))
    crsm = finimage.movecursor
    crss = finimage.setcursor
    generates([[
            {"type":"combiner","rotate":2,"weld":[True]*4,"data":None}, 
            {"type":"transistor","rotate":1,"weld":[True]*4,"data":None}
            ]], pthname='cache/combinerimg.png', ratio=4)
    generates([[
            {"type":"extractor","rotate":2,"weld":[True]*4,"data":None}, 
            {"type":"transistor","rotate":1,"weld":[True]*4,"data":None}
            ]], pthname='cache/extractorimg.png', ratio=4)
    combinerimg = Image.open("cache/combinerimg.png")
    extractorimg = Image.open("cache/extractorimg.png")
    typfound = {}
    for typ in returned.keys():
        if name in returned[typ]:
            print(f"{typ}: {returned[typ][name]}")
            typfound[typ] = returned[typ][name]
            
    amountimgtable = {}
    for typ, multientri in typfound.items():
        match typ:
            case "combine":
                for num, entri in enumerate(multientri):
                    generates(entri['grid'], num, name)
                    img = Image.new("RGBA", (128, 640))
                    generates([[
                    {"type":entri['block'],"rotate":0,"weld":[True]*4,"data":None}
                    ]], pthname="cache/amount.png", ratio=4)
                    for i in range(entri['amount']):
                        img.alpha_composite(
                            Image.open("cache/amount.png"),
                            (i%2*64, i//2*64)
                        )
                    amountimgtable[num] = cropempty(img)
                    print()
                for recipenum in range(0, 99):
                    md = (0, 0)
                    pthf = glob.glob(f"cache/recipeframe-{name}-{recipenum}*.png")
                    if len(pthf) == 0: break
                    print(f"{name} {recipenum} has {len(pthf)}")
                    frmct = []
                    for pth in pthf:
                        img = Image.open(pth)
                        frmct.append(img)
                        md = gif.tuple_max(md, img.size)
                    print(f"product dm = {md}")
                    productimg = amountimgtable[recipenum]
                    finimage.addgifframes(frmct)
                    crss(x=0)
                    finimage.addimageframes(combinerimg, movecursor=False)
                    crsm(x=md[0]+64, y=-md[1])
                    finimage.addimageframes(
                        getarrowimg('combiner'), movecursor=False,
                        pos=sumtuple(finimage.cursor, (0, md[1]//2)))
                    crsm(x=128)
                    finimage.addimageframes(productimg)
                    if productimg.height < md[0]:
                        crsm(y=md[0]-productimg.height-64)
                    crss(x=0)
                    crsm(y=32)
            case "extract":
                amountimgtable = {}
                print("EXTRACT RECIPE")
                for num, entri in enumerate(multientri):
                    generates([[entri['ingredient']]], num, name, pthname=f"cache/extract-{name}-{num}.png")
                    img = Image.new("RGBA", (128, 640))
                    generates([[
                    {"type":name,"rotate":0,"weld":[True]*4,"data":None}
                    ]], pthname="cache/amount.png", ratio=4)
                    for i in range(entri['amount']):
                        img.alpha_composite(
                            Image.open("cache/amount.png"),
                            (i%2*64, i//2*64)
                        )
                    amountimgtable[num] = cropempty(img)
                    print()
                for recipenum in range(0, 99):
                    md = (64, 64)
                    pthf = glob.glob(f"cache/extract-{name}-{recipenum}.png")
                    if len(pthf) == 0: break
                    img = Image.open(pthf[0])
                    md = gif.tuple_max(md, img.size)
                    productimg = amountimgtable[recipenum]
                    finimage.addimageframes(img)
                    crss(x=0)
                    finimage.addimageframes(extractorimg, movecursor=False)
                    crsm(x=md[0]+128, y=-md[1])
                    finimage.addimageframes(
                        getarrowimg('extractor'), movecursor=False,
                        pos=sumtuple(finimage.cursor, (0, md[1]//2)))
                    crsm(x=128)
                    finimage.addimageframes(productimg)
                    crss(x=0)
                    crsm(y=64+32)
        
    finimage.export(f"cache/recipe-{name}.gif", apng=apng)
    return typfound
    


if __name__ == "__main__":
    generaterecipe("galvanometer", apng=True)
    generaterecipe("pulp")
    # generaterecipe("air")
    # generaterecipe("destroyer")
    generaterecipe("compressed_stone")
    generaterecipe("inductor")
    # generaterecipe(returned, "galvanometer")
    # generaterecipe(returned, "potentiometer")
    # generaterecipe(returned, "galvanometer")
    # generaterecipe(returned, "prism")
    for maderecipecache in glob.glob(f"cache/recipeframe-*.png"):
        try: os.remove(maderecipecache)
        except: pass
