import pyfunc.smp as smp
import collections
import copy
import json
from pyfunc.assetload import assetinit,blockinfos
assetinit()
from pyfunc.block import BlockDataIn
import typing
import schema # type: ignore # no type hints

def getblocksbyattr(attr:str) -> list[str]:
    return [b for b,data in blockinfos.items() if attr in data['attributes']]

def getblocksbycollision(collision:str) -> list[str]:
    return [b for b,data in blockinfos.items() if collision in data['collision']]

with open("content/recipes.smp") as f:
    rawdata = smp.getsmpvalue(f.read())

data=collections.defaultdict(list)

for x in rawdata:
    x=copy.deepcopy(x)
    typ=x['type']
    data[typ].append(x)

Research = typing.NewType('Research', str)
Passive = typing.NewType('Passive', str)

Tag:typing.TypeAlias = list[str]

tags:dict[str,Tag]={}

def fixemptygrid(g:str|list[list[BlockDataIn]]) -> list[list[BlockDataIn]]:
    if isinstance(g,str):
        if g == '':
            return [[]]
        else:
            raise ValueError('bad grid')
    return g

def handlepos(p:str) -> tuple[int,int]:
    x,y = p.split(',')
    return (int(x),int(y))

def strtobool(s:str) -> bool:
    assert s in ['0','1']
    return s == '1'

def assertblock(s:str) -> BlockDataIn:
    assert s[0] != '$'
    if s == 'NIC':
        return 'air'
    assert s.split()[0] in blockinfos
    if ' display_facing ' in s:
        b,_,d = s.split()
        rotation = {
            'up':0,
            'down':2,
            'east':3,
            'west':1,
        }[d]
        return {'type':b,'rotate':rotation}
    if s.split() == ['foam','needs_container_count5']:
        return {'type':'foam','offsetx':32}
    if s.split() == ['dirt','grassy']:
        return {'type':'dirt','offsetx':64}
    if s.split() == ['spark_catcher','needs_container_count5']:
        return {'type':'spark_catcher','data':'5'}
    assert ' ' not in s
    return s

def assertblockstr(s:str) -> str:
    assert s[0] != '$'
    if s == 'NIC':
        return 'air'
    assert s.split()[0] in blockinfos
    assert ' ' not in s
    return s

def assertresearch(s:str) -> Research:
    assert True
    return Research(s)

def handlespecialblock(s:str) -> list[BlockDataIn]:
    try:
        return [assertblock(s)]
    except AssertionError:
        if s.split()[0] in ['any','non_air']:
            typ,filtertype,filtervalue = s.split()
            assert filtertype in ['needs_attribute','needs_collision']
            if filtertype == 'needs_attribute':
                blocks = getblocksbyattr(filtervalue)
            if filtertype == 'needs_collision':
                blocks = getblocksbycollision(filtervalue)
            if typ == 'non_air':
                blocks = [b for b in blocks if b != 'air']
            return typing.cast(list[BlockDataIn],blocks) # list[str] can't auto cast to list[str | other stuff]
        raise ValueError(f'"{s}" is not a block')

def asserttags(s:str) -> list[BlockDataIn] | BlockDataIn:
    s2 = handletags(s)
    if isinstance(s2,str):
        l = handlespecialblock(s2)
    else:
        l = [x for b in s2 for x in handlespecialblock(b)]
    if len(l) == 1:
        return l[0]
    return l

block = schema.Use(assertblock)
research = schema.Use(assertresearch)
blocktag = schema.Use(asserttags)
num = schema.Use(int)
flag = schema.Use(strtobool)

tagschema:schema.Schema = schema.Schema([{
    'type':'tag',
    'name':str,
    'blocks':[schema.Use(assertblockstr)]
}])

tagdata = tagschema.validate(data['tag'])

for tag in data['tag']:
    assert tag['name'] not in tags
    assert isinstance(tag['blocks'],list)
    tags[tag['name']]=typing.cast(Tag, tag['blocks'])

def handletags(s:str) -> str | list[str]:
    if s.startswith('$'):
        s,*extra = s.split()
        if s[1:] in tags:
            if len(extra)==0:
                return tags[s[1:]]
            return [' '.join([x,*extra]) for x in tags[s[1:]]]
        print(f'{s} is Just a Normal name starts with $ ???????')
    return s

# filters:
# grassy
# non_air
# needs_collision
# buildable
# not_water
# needs_container_count5

dataschema = schema.Schema({
    'tag':[{
        'type':'tag',
        'name':str,
        'blocks':[block]
    }],
    'heat':[{
        'type':'heat',
        'product':block,
        'ingredient':blocktag,
        'time':num,
        schema.Optional('needs_entity',default = False):flag,
        schema.Optional('surrounding'):{
            'block':block,
            'minimum':num,
        },
    }],
    'extract':[{
        'type':'extract',
        'product':block,
        'amount':num,
        'ingredient':blocktag,
        'time':num,
        schema.Optional('post_action'):schema.Or('destroy','reduce_container_count5')
    }],
    'inject':[{
        'type':'inject',
        'product':schema.Or(
            {
                'transform_receiver':block
            },
            {
                'fertilizer':flag
            }
        ),
        'pill':block,
        'receiver':block,
        schema.Optional('needs_passive'):research
    }],
    'combine':[{
        'type':'combine',
        'grid':[[blocktag]],
        'product':{
            'block':block,
            'amount':num,
        },
        schema.Optional('needs_passive'):research
    }],
    'extra_display':[{
        'type':'extra_display',
        'grid':schema.Or(schema.Use(fixemptygrid),[[blocktag]]),
        'product':{
            'filter':blocktag,
            schema.Optional('amount',default = 1):num,
        },
        schema.Optional('arrow_sprite',default = 0):num,
        schema.Optional('guidebook_page_blacklist',default = []):[block], # don't put this on these pages, even if the recipe contains those blocks
        schema.Optional('guidebook_page_whitelist',default = []):[block], # put this on these pages, even if the recipe doesn't contain those blocks
        schema.Optional('weldall',default = True):flag, # weld all blocks?
        schema.Optional('needs_passive'):research,
        schema.Optional('research_requirement_override'):research, # the research that makes  this "recipe" appear in the guidebook
        schema.Optional('entity'):{
            'type':str,
            'position':schema.Use(handlepos)
        },
        schema.Optional('guidebook_use_only',default = False):flag,
        schema.Optional('match_filter_modulo',default = False):flag, # true if the changing blocks all match
    }],
    'summonore_pill':[{
        'type':'summonore_pill',
        'filter':blocktag
    }],
    'sensor_natural':[{
        'type':'sensor_natural',
        'filter':blocktag
    }],
    'sensor_rare_resource':[{
        'type':'sensor_rare_resource',
        'filter':blocktag
    }],
})

data=dataschema.validate(data)

class SurroundingBlock(typing.TypedDict):
    block:BlockDataIn
    minimum:int

class Product(typing.TypedDict):
    block:BlockDataIn
    amount:int

class EntityPos(typing.TypedDict):
    type:str
    position:tuple[int,int]

class FilterProduct(typing.TypedDict):
    filter:BlockDataIn | Tag
    amount:int

class HeatRecipe(typing.TypedDict):
    product:BlockDataIn
    ingredient:BlockDataIn | Tag
    time:int
    needs_entity:bool
    surrounding:typing.NotRequired[SurroundingBlock]

class ExtractRecipe(typing.TypedDict):
    product:BlockDataIn
    amount:int
    ingredient:BlockDataIn | Tag
    time:int
    post_action:typing.NotRequired[str]

class InjectRecipe(typing.TypedDict):
    product:BlockDataIn | typing.Literal['__fertilizer']
    pill:BlockDataIn
    receiver:BlockDataIn
    needs_passive:typing.NotRequired[Passive]

class CombineRecipe(typing.TypedDict):
    grid:list[list[BlockDataIn | Tag]]
    amount:int
    needs_passive:typing.NotRequired[Passive]

class ExtraDisplayRecipe(typing.TypedDict):
    grid:list[list[BlockDataIn | Tag]]
    amount:int
    arrow_sprite:int
    guidebook_page_blacklist:list[str] # don't put this on these pages, even if the recipe contains those blocks
    guidebook_page_whitelist:list[str] # put this on these pages, even if the recipe doesn't contain those blocks
    weldall:bool # weld all blocks?
    needs_passive:typing.NotRequired[Passive]
    research_requirement_override:typing.NotRequired[Research] # the research that makes  this "recipe" appear in the guidebook
    entity:typing.NotRequired[EntityPos]
    guidebook_use_only:bool
    match_filter_modulo:bool # true if the changing blocks all match

heat:dict[str,list[HeatRecipe]]=collections.defaultdict(list)
for hrecipe in data['heat']:
    heat[hrecipe['product']].append(hrecipe)
    del hrecipe['product']
    del hrecipe['type']

extract:dict[str,list[ExtractRecipe]] = collections.defaultdict(list)
for erecipe in data['extract']:
    extract[erecipe['product']].append(erecipe)
    del erecipe['product']
    del erecipe['type']

inject:dict[str,list[InjectRecipe]] = collections.defaultdict(list)
for irecipe in data['inject']:
    product = irecipe['product']
    if 'fertilizer' in product and product['fertilizer']:
        key = '__fertilizer'
    else:
        key = product['transform_receiver']
    inject[key].append(irecipe)
    del irecipe['product']
    del irecipe['type']

combine:dict[str,list[CombineRecipe]] = collections.defaultdict(list)
for crecipe in data['combine']:
    product = crecipe['product']
    crecipe['amount'] = product['amount']
    combine[product['block']].append(crecipe)
    del crecipe['product']
    del crecipe['type']

extra_display:dict[str,list[ExtraDisplayRecipe]] = collections.defaultdict(list)
for erecipe in data['extra_display']:
    product = erecipe['product']
    erecipe['amount'] = product['amount']
    if isinstance(product['filter'],list):
        out = product['filter']
    elif isinstance(product['filter'],dict):
        out = [product['filter']['type']]
    else:
        out = [product['filter']]
    del erecipe['type']
    for p in out:
        erecipe = copy.deepcopy(erecipe)
        erecipe['product'] = p
        extra_display[p].append(erecipe)

summonore_pill:set[str] = set()
for srecipe in data['summonore_pill']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        summonore_pill.add(p)

sensor_natural:set[str] = set()
for srecipe in data['sensor_natural']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        sensor_natural.add(p)

sensor_rare_resource:set[str] = set()
for srecipe in data['sensor_rare_resource']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        sensor_rare_resource.add(p)

with open('data.json','w') as f:
    json.dump(data,f,indent = 2)