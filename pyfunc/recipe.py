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

def getarrowimg(name:str) -> Image.Image:
    icox, icoy = getarrowcoords()[name]
    return Image.open(
        cfgstr("localGame.texture.guidebookArrowFile")).crop(
            (16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))
        ).resize((64, 64), Image.NEAREST
    )

def addentries(i:dict[str, Any], entryname:str, typ:str, organdict:dict, includekeysstr:str) -> None:
    includekeys = massstrip(includekeysstr.split(','))
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

# heat
# extract
# inject
# combine
# extra_display
# summonore_pill

def generaterecipe(name:str) -> None:
    if name in combine:
        gridpos = combine[name]
        results:list[dict] = []
        for i,recipe in enumerate(gridpos):
            imgs=generates(recipe['grid'],ratio=4)
            result=[{"type":name,"rotate":0,"weld":noweld,"data":None}]*recipe['amount']
            img=generates(typing.cast(list[list[BlockDataIn]],[*batched(result,2)]),ratio=4,assertconnected=False)[0] # batched makes 2 columns automatically
            results.append({'recipeframes':imgs,'result':img})
        bg = cfg("recipeSetting.recipeBackground")
        assert isinstance(bg,list)
        finimage = gif.gif(tuple(bg))
        combiner=generates([[
            {"type":"combiner","rotate":2,"weld":fullweld}, 
            {"type":"transistor","rotate":1,"weld":fullweld}
        ]],ratio=4)[0]
        maxdim = tuple_max((64*2, 0),*[img.size for recipeimgs in results for img in recipeimgs['recipeframes']]) # fancy double iteration # the recipe is at least 2 blocks wide
        y = 0
        ymargin = cfg("recipeSetting.recipeMarginY")
        assert isinstance(ymargin,int)
        for recipeimgs in results:
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
                h +     # the recipe height
                64 +    # the combiner
                ymargin # mandatory gap between recipes
            )
        finimage.export(f"cache/recipe-{name}.gif")


if __name__ == "__main__":
    generaterecipe("galvanometer")
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
