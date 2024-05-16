import PIL.Image
import collections
import glob
import os
from PIL import Image
import pyfunc.gif as gif
from typing import Any
from pyfunc.datafunc import tuple_max, tuple_min
from pyfunc.lang import cfg, getarrowcoords
from pyfunc.smp import getsmpvalue
from pyfunc.block import canweld, get, makeimage, bottomtypes, topbottomtypes, sidestypes, notoptypes, norotatetypes, twowaytypes, normalize, makeweldside
import itertools
import logging
from pyfunc.recipeprocess import heat, extract, inject, combine, extra_display, summonore_pill

l = logging.getLogger()

noweld = (makeweldside(False),) * 4
fullweld = (makeweldside(True),) * 4

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

# the parts that are always the same
combiner=generates([[
    {"type":"combiner","rotate":2,"weld":fullweld,"data":None}, 
    {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
]],ratio=4)[0]
extractor=generates([[
    {"type":"extractor","rotate":2,"weld":fullweld,"data":None}, 
    {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
]],ratio=4)[0]

def generaterecipe(name) -> None:
    finimage = gif.gif(tuple(cfg("recipeSetting.recipeBackground")))
    results:list[dict] = []
    if name in combine:
        crecipes = combine[name]
        for i,recipe in enumerate(crecipes):
            imgs=generates(recipe['grid'],ratio=4)
            _,h = gif.tuple_max((64*2, 0),*[img.size for img in imgs])
            anim = gif.gif((0,0,0)) # the color is ignored
            anim.addgifframes(
                imgs,
                pos=(0, 0)
            )
            anim.addimageframes(
                combiner,
                pos=(0, h)
            )
            result=[{"type":name,"rotate":0,"weld":noweld,"data":None}]*recipe['amount']
            img=generates([*itertools.batched(result,2)],ratio=4,assertconnected=False)[0] # batched makes 2 columns automatically
            results.append({'anim':anim,'arrowsprite':'combiner','result':img})
    if name in extract:
        erecipes = extract[name]
        for i,recipe in enumerate(erecipes):
            imgs=generates([[recipe['ingredient']]],ratio=4)
            _,h = gif.tuple_max((64*2, 0),*[img.size for img in imgs])
            anim = gif.gif((0,0,0)) # the color is ignored
            anim.addgifframes(
                imgs,
                pos=(0, 0)
            )
            anim.addimageframes(
                extractor,
                pos=(0, h)
            )
            result=[{"type":name,"rotate":0,"weld":noweld,"data":None}]*recipe['amount']
            img=generates([*itertools.batched(result,2)],ratio=4,assertconnected=False)[0] # batched makes 2 columns automatically
            results.append({'anim':anim,'arrowsprite':'combiner','result':img})
    maxdim = tuple_max((0, 0),*[recipeimgs['anim'].getsize() for recipeimgs in results])
    y = 0
    for recipeimgs in results:
        _,h = recipeimgs['anim'].getsize()
        finimage.addgif(
            recipeimgs['anim'],
            pos = (0, y),
        )
        finimage.addimageframes(
            recipeimgs['result'],
            pos=(maxdim[0]+64+64+64, y)
        )
        finimage.addimageframes(
            getarrow(recipeimgs['arrowsprite']),
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
    # generaterecipe("galvanometer")
    # generaterecipe("potentiometer")
    # generaterecipe("galvanometer")
    # generaterecipe("prism")
    for maderecipecache in glob.glob(f"cache/recipeframe-*.png"):
        try: os.remove(maderecipecache)
        except: pass
