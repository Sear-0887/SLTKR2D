import pyfunc.smp as smp
import collections
import copy
import json
from pyfunc.assetload import assetinit,blockinfos
assetinit()
from pyfunc.block import BlockDataIn
import typing
import schema # type: ignore # no type hints

with open("content/recipes.smp") as f:
    rawdata = smp.getsmpvalue(f.read())

data=collections.defaultdict(list)

for x in rawdata:
    x=copy.deepcopy(x)
    typ=x['type']
    data[typ].append(x)

print(json.dumps({dk:[*set([k for x in d for k in x.keys()])] for dk,d in data.items()},indent=2))

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
        if s.split()[0] == 'any':
            _,filtertype,filtervalue = s.split()
            assert filtertype in ['needs_attribute','needs_collision']
            if filtertype == 'needs_attribute':
            if filtertype == 'needs_collision':
        raise ValueError(f'"{s}" is not a block')

def asserttags(s:str) -> list[BlockDataIn] | BlockDataIn:
    s2 = handletags(s)
    if isinstance(s2,str):
        return handlespecialblock(s2)
    return [handlespecialblock(b) for b in s2]

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

class HeatRecipe(typing.TypedDict):
    product:BlockDataIn
    ingredient:BlockDataIn | Tag
    time:int
    needs_entity:bool
    surrounding:typing.NotRequired[SurroundingBlock]

class ExtractRecipe(typing.TypedDict):
    pass

class InjectRecipe(typing.TypedDict):
    pass

class CombineRecipe(typing.TypedDict):
    pass

class ExtraDisplayRecipe(typing.TypedDict):
    pass

class SummonorePillRecipe(typing.TypedDict):
    pass

class SensorNaturalRecipe(typing.TypedDict):
    pass

class SensorRareResourceRecipe(typing.TypedDict):
    pass


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
{
    'type':'extract',
    'product':block,
    'amount':num,
    'ingredient':blocktag,
    'time':num,
    schema.Optional('post_action'):schema.Or('destroy','reduce_container_count5')
}
inject:dict[str,list[InjectRecipe]] = collections.defaultdict(list)
for irecipe in data['inject']:
    inject[irecipe['product']].append(irecipe)
    del irecipe['product']
    del irecipe['type']
{
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
}
combine:dict[str,list[CombineRecipe]] = collections.defaultdict(list)
for crecipe in data['combine']:
    combine[crecipe['product']].append(crecipe)
    del crecipe['product']
    del crecipe['type']
{
    'type':'combine',
    'grid':[[blocktag]],
    'product':{
        'block':block,
        'amount':num,
    },
    schema.Optional('needs_passive'):research
}
extra_display:dict[str,list[ExtraDisplayRecipe]] = collections.defaultdict(list)
for erecipe in data['extra_display']:
    extra_display[erecipe['product']].append(erecipe)
    del erecipe['product']
    del erecipe['type']
{
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
}
summonore_pill:dict[str,list[SummonorePillRecipe]] = collections.defaultdict(list)
for srecipe in data['summonore_pill']:
    summonore_pill[srecipe['product']].append(srecipe)
    del srecipe['product']
    del srecipe['type']
{
    'type':'summonore_pill',
    'filter':blocktag
}
sensor_natural:dict[str,list[SensorNaturalRecipe]] = collections.defaultdict(list)
for srecipe in data['sensor_natural']:
    sensor_natural[srecipe['product']].append(srecipe)
    del srecipe['product']
    del srecipe['type']
{
    'type':'sensor_natural',
    'filter':blocktag
}
sensor_rare_resource:dict[str,list[SensorRareResourceRecipe]] = collections.defaultdict(list)
for srecipe in data['sensor_rare_resource']:
    sensor_rare_resource[srecipe['product']].append(srecipe)
    del srecipe['product']
    del srecipe['type']
{
    'type':'sensor_rare_resource',
    'filter':blocktag
}

with open('data.json','w') as f:
    json.dump(data,f,indent = 2)