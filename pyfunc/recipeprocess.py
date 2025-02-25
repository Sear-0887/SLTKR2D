import pyfunc.smp as smp
import collections
import copy
from pyfunc.lang import openCfgPath
from pyfunc.assetload import blockinfos
from pyfunc.block import BlockDataIn
import typing
import schema # type: ignore[import-untyped] # no type hints

def getblocksbyattr(attr:str) -> list[str]:
    return [b for b,data in blockinfos.items() if attr in data['attributes']]

def getblocksbycollision(collision:str) -> list[str]:
    return [b for b,data in blockinfos.items() if collision in data['collision']]

Research = typing.NewType('Research', str)
Passive = typing.NewType('Passive', str)

Tag:typing.TypeAlias = list[str]

tags:dict[str,Tag]={}

def fixemptygrid(g:str|list[list[BlockDataIn]]) -> list[list[BlockDataIn]]:
    if isinstance(g,str):
        if g == '':
            return [['air']]
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
        print(s)
        if s.split()[0] in ['any','non_air']:
            nowater = False
            if 'not_water' in s:
                s = s.replace('not_water','')
                nowater = True
            typ,filtertype,filtervalue = s.split()
            assert filtertype in ['needs_attribute','needs_collision']
            if filtertype == 'needs_attribute':
                blocks = getblocksbyattr(filtervalue)
            if filtertype == 'needs_collision':
                blocks = getblocksbycollision(filtervalue)
            if typ == 'non_air':
                blocks = [b for b in blocks if b != 'air']
            if nowater:
                blocks = [b for b in blocks if b != 'water']
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
        'grid':schema.And(schema.Use(fixemptygrid),[[blocktag]]),
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

class SurroundingBlock(typing.TypedDict):
    block:BlockDataIn
    minimum:int

class EntityPos(typing.TypedDict):
    type:str
    position:tuple[int,int]

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

class SummonorePillRecipe(typing.TypedDict):
    filter:BlockDataIn | Tag

class SensorNaturalRecipe(typing.TypedDict):
    filter:BlockDataIn | Tag

class SensorRareResourceRecipe(typing.TypedDict):
    filter:BlockDataIn | Tag

heat:dict[str,list[HeatRecipe]]=collections.defaultdict(list)
extract:dict[str,list[ExtractRecipe]] = collections.defaultdict(list)
inject:dict[str,list[InjectRecipe]] = collections.defaultdict(list)
combine:dict[str,list[CombineRecipe]] = collections.defaultdict(list)
extra_display:dict[str,list[ExtraDisplayRecipe]] = collections.defaultdict(list)
summonore_pill:set[str] = set()
sensor_natural:set[str] = set()
sensor_rare_resource:set[str] = set()

with openCfgPath('localGame.texture.recipesFile') as f:
    rawdata = smp.getsmpvalue(f.read())

assert isinstance(rawdata,list)

del f

data=collections.defaultdict(list)

for x in rawdata:
    assert isinstance(x,dict)
    typ=x['type']
    data[typ].append(x)

del x
del rawdata

tagdata = tagschema.validate(data['tag'])

for tag in tagdata:
    assert tag['name'] not in tags
    assert isinstance(tag['blocks'],list)
    tags[tag['name']]=typing.cast(Tag, tag['blocks'])

del tag
del tagdata

class RecipeData:
    heat:list[HeatRecipe]
    extract:list[ExtractRecipe]
    inject:list[InjectRecipe]
    combine:list[CombineRecipe]
    extra_display:list[ExtraDisplayRecipe]
    summonore_pill:list[SummonorePillRecipe]
    sensor_natural:list[SensorNaturalRecipe]
    sensor_rare_resource:list[SensorRareResourceRecipe]

dataval=dataschema.validate(data)
del data

for hrecipe in dataval['heat']:
    heat[hrecipe['product']].append(hrecipe)
    del hrecipe['product']
    del hrecipe['type']

for erecipe in dataval['extract']:
    extract[erecipe['product']].append(erecipe)
    del erecipe['product']
    del erecipe['type']

for irecipe in dataval['inject']:
    product = irecipe['product']
    if 'fertilizer' in product and product['fertilizer']:
        key = '__fertilizer'
    else:
        key = product['transform_receiver']
    inject[key].append(irecipe)
    del irecipe['product']
    del irecipe['type']

for crecipe in dataval['combine']:
    product = crecipe['product']
    crecipe['amount'] = product['amount']
    combine[product['block']].append(crecipe)
    del crecipe['product']
    del crecipe['type']

for erecipe in dataval['extra_display']:
    product = erecipe['product']
    erecipe['amount'] = product['amount']
    if isinstance(product['filter'],list):
        out = product['filter']
    else:
        out = [product['filter']]
    del erecipe['type']
    for p in out:
        if isinstance(p,dict):
            idx = p['type']
        else:
            idx = p
        if len(erecipe['guidebook_page_whitelist']) != 0:
            if idx not in erecipe['guidebook_page_whitelist']:
                continue
        if len(erecipe['guidebook_page_blacklist']) != 0:
            if idx in erecipe['guidebook_page_blacklist']:
                continue
        erecipe = copy.deepcopy(erecipe)
        erecipe['product'] = p
        extra_display[idx].append(erecipe)

for srecipe in dataval['summonore_pill']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        summonore_pill.add(p)

del p

for srecipe in dataval['sensor_natural']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        sensor_natural.add(p)

for srecipe in dataval['sensor_rare_resource']:
    if isinstance(srecipe['filter'],list):
        out = srecipe['filter']
    elif isinstance(srecipe['filter'],dict):
        out = [srecipe['filter']['type']]
    else:
        out = [srecipe['filter']]
    for p in out:
        sensor_rare_resource.add(p)

del hrecipe
del irecipe
del crecipe
del erecipe
del srecipe