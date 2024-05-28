import PIL.Image
import collections
import glob
import os
from PIL import Image
import pyfunc.gif as gif
from typing import Any, TypeVar, Callable
import typing
from pyfunc.datafunc import tuple_max, tuple_min
from pyfunc.lang import cfg, cfgstr, getarrowcoords
from pyfunc.smp import getsmpvalue
from pyfunc.block import canweld, get, makeimage, bottomtypes, topbottomtypes, sidestypes, notoptypes, norotatetypes, twowaytypes, normalize, makeweldside, BlockDataIn, BlockData
import itertools
import logging
from pyfunc.recipeprocess import heat, extract, inject, combine, extra_display, summonore_pill

T1 = TypeVar('T1')
T2 = TypeVar('T2')

if hasattr(itertools,'batched'):
    def batched(l:list[T1],n:int) -> typing.Iterable[list[T1]]:
        return map(list,itertools.batched(l,n))
else:
    def batched(l:list[T1],n:int) -> typing.Iterable[list[T1]]:
        return map(list,itertools.zip_longest(*[itertools.islice(l,i,None,n) for i in range(n)]))

l = logging.getLogger()

noweld = (makeweldside(False),) * 4
fullweld = (makeweldside(True),) * 4

def generates(grid1:list[list[BlockDataIn]],ratio:int,assertconnected:bool=True) -> list[Image.Image]:
    tags=[]
    for y,row in enumerate(grid1):
        for x,block in enumerate(row):
            if isinstance(block, list): # If it's a list, it's a tag, which
                tags.append([(x,y,normalize(t)) for t in block])
                grid1[y][x] = normalize(block[0]) # Actions
            elif isinstance(block, str): # It's normal and needed to NORMALIZE
                grid1[y][x] = normalize(block) # Actions
    grid:list[list[BlockData]] = typing.cast(list[list[BlockData]],grid1)
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

def doublemap(f:Callable[[T1],T2],ll:list[list[T1]]) -> list[list[T2]]:
    return [[f(x) for x in l] for l in ll]

def isblock(b:BlockData) -> bool:
    return b['type'] != 'air'

def genimage(generated:list[list[BlockData]],assertconnected:bool=True) -> Image.Image:
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
    def floodfill() -> bool:
        filled=set([(0,0)])
        edgeblocks=[(0,0)] # the blocks that are welded to a filled block
        sideinfo=[ # do not change
            ('right','left', +1,  0),
            ('left','right', -1,  0),
            ('bottom','top',  0, +1),
            ('top','bottom',  0, -1),
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
    gen = makeimage(typing.cast(list[list[BlockDataIn]],generated)) # Make Image # the cast is to appease mypy
    return gen

def getarrow(typ:str) -> Image.Image:
    icox, icoy = getarrowcoords()[typ]
    return Image.open(
        cfgstr("localGame.texture.guidebookArrowFile")
    ).crop(
        (16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))
    ).resize(
        (64, 64), Image.NEAREST
    )

# heat yes
# extract yes
# inject
# combine yes
# extra_display

# the parts that are always the same
combiner=generates([[
    {"type":"combiner","rotate":2,"weld":fullweld,"data":None}, 
    {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
]],ratio=4)[0]
extractor=generates([[
    {"type":"extractor","rotate":2,"weld":fullweld,"data":None}, 
    {"type":"transistor","rotate":1,"weld":fullweld,"data":None}
]],ratio=4)[0]
arc_furnace=generates([[
    {"type":"arc_furnace","rotate":0,"weld":fullweld,"data":None}
]],ratio=4)[0]

def generaterecipe(name:str) -> None:
    finimage = gif.gif(tuple(cfg("recipeSetting.recipeBackground")))
    results:list[dict] = []
    print('generating recipe for',name)
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
            results.append({'anim':anim,'arrowsprite':'extractor','result':img})
    if name in heat:
        print(name,'in heat')
        hrecipes = heat[name]
        for i,recipe in enumerate(hrecipes):
            row = [recipe['ingredient']]
            furnacex = 0
            if 'surrounding' in recipe:
                # to the right and then to the left
                count = recipe['surrounding']['minimum']
                block = recipe['surrounding']['block']
                if count >= 1:
                    row += [block]
                if count >= 2:
                    row = [block] + row
                    furnacex = 64
                if count >= 3:
                    raise ValueError('no support for 3 surrounding')
            imgs=generates([row],ratio=4,assertconnected=False)
            _,h = gif.tuple_max((64*2, 0),*[img.size for img in imgs])
            anim = gif.gif((0,0,0)) # the color is ignored
            anim.addgifframes(
                imgs,
                pos=(0, 0)
            )
            anim.addimageframes(
                arc_furnace,
                pos=(furnacex, h)
            )
            img=generates([[name]],ratio=4)[0]
            results.append({'anim':anim,'arrowsprite':'arc_furnace','result':img})
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
    generaterecipe("galvanometer")
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
