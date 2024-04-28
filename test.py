import pyfunc.smp as smp
import collections
import copy
import json
from pyfunc.assetload import assetinit,blockinfos
assetinit()

with open("content/recipes.smp") as f:
    rawdata = smp.getsmpvalue(f.read())

data=collections.defaultdict(list)

for x in rawdata:
    x=copy.deepcopy(x)
    typ=x['type']
    data[typ].append(x)

print(json.dumps({dk:[*set([k for x in d for k in x.keys()])] for dk,d in data.items()},indent=2))

tags={}

for tag in data['tag']:
    tag=copy.deepcopy(tag)
    name=tag['name']
    del tag['name']
    assert name not in tags
    tags[name]=tag['blocks']

def handletags(s:str) -> str | list:
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

import schema

def fixemptygrid(g):
    if g == '':
        return [[]]
    else:
        raise ValueError('bad grid')

def handlepos(p):
    x,y = p.split(',')
    return (int(x),int(y))

def strtobool(s):
    assert s in ['0','1']
    return s == '1'

def assertblock(s):
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

def assertresearch(s):
    assert True
    return s

def handlespecialblock(s):
    try:
        return assertblock(s)
    except AssertionError:
        print(f'"{s}" is not a block')

def asserttags(s):
    s = handletags(s)
    if isinstance(s,str):
        return handlespecialblock(s)
    return [handlespecialblock(b) for b in s]

block = schema.Use(assertblock)
research = schema.Use(assertresearch)
blocktag = schema.Use(asserttags)
num = schema.Use(int)
flag = schema.Use(strtobool)

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
        schema.Optional('arrow_sprite'):num,
        schema.Optional('guidebook_page_blacklist',default = []):[block], # don't put this on 
        schema.Optional('guidebook_page_whitelist',default = []):[block],
        schema.Optional('weldall',default = True):flag,
        schema.Optional('needs_passive'):research,
        schema.Optional('research_requirement_override'):research,
        schema.Optional('entity'):{
            'type':str,
            'position':schema.Use(handlepos)
        },
        schema.Optional('guidebook_use_only',default = False):flag,
        schema.Optional('match_filter_modulo'):flag, # the changing blocks all match
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

data2=dataschema.validate(data)

with open('data.json','w') as f:
    json.dump(data2,f,indent = 2)