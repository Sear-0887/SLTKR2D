import PIL.Image
import collections
import glob
import os
from PIL import Image
import pyfunc.gif as gif
from typing import Any
from pyfunc.datafunc import tuple_max, tuple_min
from pyfunc.lang import botinit, cfg, getarrowcoords
from pyfunc.smp import getsmpvalue
from pyfunc.block import canweld, get, makeimage, bottomtypes, topbottomtypes, sidestypes, notoptypes, norotatetypes, twowaytypes, normalize, makeweldside
import itertools
import logging

l = logging.getLogger()

noweld = (makeweldside(False),) * 4
fullweld = (makeweldside(True),) * 4

def massstrip(l:list[str]) -> list[str]:
    return [s.strip() for s in l]

def handletags(s:str, organdict:dict) -> str | list:
    if not isinstance(s, str): return s 
    s = s.split(" ")[0]
    if s.startswith('$'):
        if s[1:] in organdict['tag'].keys():
            return organdict['tag'][s[1:]]
        l.warning(f'{s} is Just a Normal name starts with $ ???????')
    return s

def handlegridtags(s:list[list[str]], organdict:dict) -> list[list[str | list]]:
    return [
        [
            handletags(critem, organdict)
            for critem in row
        ]
        for row in s
    ]

def getarrowimg(name):
    icox, icoy = getarrowcoords()[name]
    return Image.open(
        cfg("localGame.texture.guidebookArrowFile")).crop(
            (16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))
        ).resize((64, 64), Image.NEAREST
    )

def addentries(i:dict[str, Any], entryname:str, typ:str, organdict:dict, includekeys:str) -> list:
    includekeys = massstrip(includekeys.split(','))
    entries = {}
    for key, item in i.items():
        if isinstance(item, str):
            item = handletags(item, organdict)
        if isinstance(item, str) and item.isdigit(): # Handle Numbers Differently
            item = int(item)
        if typ == 'heat' and key == 'needs_entity': # True for needs_entity
            item = bool(item)
        if typ == 'combine' and key == 'grid': # Handles combine grid properties
            item = handlegridtags(item, organdict)
        i[key] = item
        if key in includekeys:
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

def generates(grid,ratio,assertconnected=True) -> list[Image.Image]:
    tags=[]
    for y,row in enumerate(grid):
        for x,block in enumerate(row):
            if isinstance(block, list): # If it's a list, it's a tag, which
                tags.append([(x,y,normalize(t)) for t in block])
                grid[y][x] = normalize(block[0]) # Actions
            elif isinstance(block, str): # It's normal and needed to NORMALIZE
                grid[y][x] = normalize(block) # Actions
    # now have a list of tags and coordinates
    ims=[]
    indices=[0 for _ in tags]
    while True:
        indices=[0 for _ in tags]
        gen=genimage(grid,assertconnected)
        width, height = gen.size # Get width, height
        gen = gen.resize((width*ratio, height*ratio), Image.NEAREST).convert("RGBA") # Resize to dimension*Ratio
        ims.append(gen)
        for i in reversed(range(len(tags))):
            indices[i]+=1
            if indices[i]>=len(tags[i]):
                indices[i]=0 # roll over
            x,y,b=tags[i][indices[i]]
            grid[y][x]=b
            if indices[i]!=0: # didn't roll over
                break
        else:
            break # all rolled over to 0 # back to the start again # but if you close your eyes, does it almost feel like we've been here before?
    return ims

def doublemap(f,ll):
    return [[f(x) for x in l] for l in ll]

def isblock(b):
    return b['type'] != 'air'

def genimage(generated,assertconnected=True):
    rotations=[]
    for y,row in enumerate(generated):
        for x,block in enumerate(row):
            if block in norotatetypes:
                continue
            elif block['type'] not in bottomtypes+topbottomtypes+sidestypes+notoptypes:
                print(f'block {block["type"]} at {x},{y} welds on all sides, does not rotate')
                # the block welds on all sides
                # no reason to check
                # wired blocks might change this
                # but would be complicated
                # would have to save all valid states and a score of how many wired blocks output onto wires
                continue
            elif block['type'] in twowaytypes:
                rotations.append([(x,y,r) for r in [0,1]]) # don't need to check all ways
            else:
                rotations.append([(x,y,r) for r in [0,2,1,3]])
    def floodfill():
        filled=set([(0,0)])
        edgeblocks=[(0,0)] # the blocks that are welded to a filled block
        sideinfo=[ # do not change
            ['right','left', +1,  0],
            ['left','right', -1,  0],
            ['bottom','top',  0, +1],
            ['top','bottom',  0, -1],
        ]
        while len(edgeblocks)>0:
            newedgeblocks=[]
            for x,y in edgeblocks:
                b=get(generated,x,y)
                for thisside,otherside,dx,dy in sideinfo:
                    if (x+dx,y+dy) not in filled and canweld(thisside,b) and canweld(otherside,get(generated,x+dx,y+dy)):
                        # spread to that block
                        newedgeblocks.append((x+dx,y+dy))
                        filled.add((x+dx,y+dy))
            edgeblocks=newedgeblocks
        return len(filled)==sum(map(sum,doublemap(isblock,generated))) # all blocks are connected
    # a ?optimized? itertools.product that changes only the ones that change in each iteration
    indices=[0 for _ in rotations]
    while True:
        if floodfill():
            break
        for i in reversed(range(len(rotations))):
            indices[i]+=1
            if indices[i]>=len(rotations[i]):
                indices[i]=0 # roll over
            x,y,r=rotations[i][indices[i]]
            generated[y][x]['rotate']=r
            if indices[i]!=0: # didn't roll over
                break
        else:
            if assertconnected:
                raise Exception('disconnected recipe') 
            # all rolled over to 0 # back to the start again 
            # # but if you close your eyes, does it almost feel like we've been here before?
            else:
                break
                
    ... 
    gen = makeimage(generated) # Make Image
    return gen

def getarrow(typ:str) -> Image.Image:
    icox, icoy = getarrowcoords()[typ]
    return Image.open(
        cfg("localGame.texture.guidebookArrowFile")
    ).crop(
        (16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))
    ).resize(
        (64, 64), Image.NEAREST
    )

# heat
# extract
# inject
# combine
# extra_display
# summonore_pill

def generaterecipe2(name) -> None:
    if name in combine:
        gridpos = combine[name]
        results:list[dict] = []
        for i,recipe in enumerate(gridpos):
            imgs=generates(recipe['grid'],ratio=4)
            result=[{"type":recipe['block'],"rotate":0,"weld":noweld,"data":None}]*recipe['amount']
            img=generates([*itertools.batched(result,2)],ratio=4,assertconnected=False)[0] # batched makes 2 columns automatically
            results.append({'recipeframes':imgs,'result':img})
        finimage = gif.gif(cfg("recipeSetting.recipeBackground"))
        combiner=generates([[
            {"type":"combiner","rotate":2,"weld":fullweld,"data":None}, 
            {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
        ]],ratio=4)[0]
        maxdim = tuple_max((64*2, 0),*[img.size for recipeimgs in results for img in recipeimgs['recipeframes']]) # fancy double iteration # the recipe is at least 2 blocks wide
        y = 0
        for recipenum,recipeimgs in enumerate(results):
            _,h = gif.tuple_max((64*2, 0),*[img.size for img in recipeimgs['recipeframes']])
            finimage.addgifframes(
                recipeimgs['recipeframes'],
                pos=(0, y)
            )
            finimage.addimageframes(
                combiner,
                pos=(0, y+h)
            )
            finimage.addimageframes(
                recipeimgs['result'],
                pos=(maxdim[0]+64+64+64, y)
            )
            finimage.addimageframes(
                getarrow("combiner"),
                pos=(maxdim[0]+64, y+h//2)
            )
            y += (
                h +                                # the recipe height
                64 +                               # the combiner
                cfg("recipeSetting.recipeMarginY") # mandatory gap between recipes
            )
        finimage.export(f"cache/recipe-{name}.gif")
    for typ in returned.keys():
        if name in returned[typ]:
            print(f"{typ}: {returned[typ][name]}")
            gridpos = returned[typ][name]
            if typ == "combine":

def generaterecipe(name) -> None:
    for typ in returned.keys():
        if name in returned[typ]:
            print(f"{typ}: {returned[typ][name]}")
            gridpos = returned[typ][name]
            if typ == "combine":
                results:list[dict] = []
                for i,recipe in enumerate(gridpos):
                    imgs=generates(recipe['grid'],ratio=4)
                    result=[{"type":recipe['block'],"rotate":0,"weld":noweld,"data":None}]*recipe['amount']
                    img=generates([*itertools.batched(result,2)],ratio=4,assertconnected=False)[0] # batched makes 2 columns automatically
                    results.append({'recipeframes':imgs,'result':img})
                finimage = gif.gif(cfg("recipeSetting.recipeBackground"))
                combiner=generates([[
                    {"type":"combiner","rotate":2,"weld":fullweld,"data":None}, 
                    {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
                ]],ratio=4)[0]
                maxdim = tuple_max((64*2, 0),*[img.size for recipeimgs in results for img in recipeimgs['recipeframes']]) # fancy double iteration # the recipe is at least 2 blocks wide
                y = 0
                for recipenum,recipeimgs in enumerate(results):
                    _,h = gif.tuple_max((64*2, 0),*[img.size for img in recipeimgs['recipeframes']])
                    finimage.addgifframes(
                        recipeimgs['recipeframes'],
                        pos=(0, y)
                    )
                    finimage.addimageframes(
                        combiner,
                        pos=(0, y+h)
                    )
                    finimage.addimageframes(
                        recipeimgs['result'],
                        pos=(maxdim[0]+64+64+64, y)
                    )
                    finimage.addimageframes(
                        getarrow("combiner"),
                        pos=(maxdim[0]+64, y+h//2)
                    )
                    y += (
                        h +                                # the recipe height
                        64 +                               # the combiner
                        cfg("recipeSetting.recipeMarginY") # mandatory gap between recipes
                    )
                finimage.export(f"cache/recipe-{name}.gif")


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
