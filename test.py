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
    del x['type']
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

heat=collections.defaultdict(list)

for h in data['heat']:
    h=copy.deepcopy(h)
    h['needs_entity'] = 'needs_entity' in h and h['needs_entity']=='1'
    product = h['product']
    del h['product']
    heat[product].append(h)

extract=collections.defaultdict(list)

for e in data['extract']:
    e=copy.deepcopy(e)
    extract[e['product']].append(e)

inject=collections.defaultdict(list)

for i in data['inject']:
    i=copy.deepcopy(i)
    if 'transform_receiver' in i['product']:
        inject[i['product']['transform_receiver']].append(i)
    else:
        inject['_fertilize'].append(i)

combine=collections.defaultdict(list)

for c in data['combine']:
    c=copy.deepcopy(c)
    product=c['product']
    del c['product']
    c['product']=product['block']
    c['amount']=product['amount']
    combine[c['product']].append(c)

extra_display=collections.defaultdict(list)

for e in data['extra_display']: # i don't want to deal with this now
    e=copy.deepcopy(e)
    product=e['product']
    del e['product']
    products = handletags(product['filter'])
    if isinstance(products,str):
        products = [products]
    for p in products:
        e2=copy.deepcopy(e)
        e2['product']=p
        e2['amount']=product.get('amount',1)
        extra_display[e2['product']].append(e2)

summonore_pill=set()

for s in data['summonore_pill']: # there is literally only one
    s=copy.deepcopy(s)
    products = handletags(s['filter'])
    if isinstance(products,str):
        products = [products]
    for p in products:
        summonore_pill.add(p)

# filters:
# grassy
# non_air
# needs_collision
# buildable
# not_water
# needs_container_count5

import schema

tagschema=schema.Schema({str:[str]})
tags = tagschema.validate(tags)

heatschema=schema.Schema({str:[{
    'ingredient':str,
    'time':schema.Use(int),
    'needs_entity':bool,
    schema.Optional('surrounding'):{
        'block':str,
        'minimum':schema.Use(int),
    },
}]})
heat = heatschema.validate(heat)

extractschema=schema.Schema({str:[{
    'product':str,
    'amount':schema.Use(int),
    'ingredient':str,
    'time':schema.Use(int),
    schema.Optional('post_action'):schema.Or('destroy','reduce_container_count5')
}]})
extract = extractschema.validate(extract)

injectschema=schema.Schema({str:[{
    'product':schema.Or(
        {
            'transform_receiver':str
        },
        {
            'fertilizer':schema.Use(int)
        }
    ),
    'pill':str,
    'receiver':str,
    schema.Optional('needs_passive'):str
}]})
inject = injectschema.validate(inject)

combineschema=schema.Schema({str:[{
    'grid':[[schema.Use(handletags)]],
    'product':str,
    'amount':schema.Use(int),
    schema.Optional('needs_passive'):str
}]})
combine = combineschema.validate(combine)

def fixemptygrid(g):
    if g == '':
        return [[]]
    else:
        raise ValueError('bad grid')

def handlepos(p):
    x,y = p.split(',')
    return (int(x),int(y))

extra_displayschema=schema.Schema({str:[{
    'grid':schema.Or(schema.Use(fixemptygrid),[[schema.Use(handletags)]]),
    'product':str,
    'amount':schema.Use(int),
    schema.Optional('arrow_sprite'):schema.Use(int),
    schema.Optional('guidebook_page_blacklist'):[str],
    schema.Optional('guidebook_page_whitelist'):[str],
    schema.Optional('weldall'):schema.Use(int),
    schema.Optional('needs_passive'):str,
    schema.Optional('research_requirement_override'):str,
    schema.Optional('entity'):{
        'type':str,
        'position':schema.Use(handlepos)
    },
    schema.Optional('guidebook_use_only'):schema.Use(int),
    schema.Optional('match_filter_modulo'):schema.Use(int),
}]})
extra_display = extra_displayschema.validate(extra_display)

summonore_pillschema=schema.Schema({str})
summonore_pill = summonore_pillschema.validate(summonore_pill)

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
        'name':str,
        'blocks':[block]
    }],
    'heat':[{
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
        'product':block,
        'amount':num,
        'ingredient':blocktag,
        'time':num,
        schema.Optional('post_action'):schema.Or('destroy','reduce_container_count5')
    }],
    'inject':[{
        'product':schema.Or(
            {
                'transform_receiver':block
            },
            {
                'fertilizer':num
            }
        ),
        'pill':block,
        'receiver':block,
        schema.Optional('needs_passive'):research
    }],
    'combine':[{
        'grid':[[blocktag]],
        'product':{
            'block':block,
            'amount':num,
        },
        schema.Optional('needs_passive'):research
    }],
    'extra_display':[{
        'grid':schema.Or(schema.Use(fixemptygrid),[[blocktag]]),
        'product':{
            'filter':blocktag,
            schema.Optional('amount',default = 1):num,
        },
        schema.Optional('arrow_sprite'):num,
        schema.Optional('guidebook_page_blacklist'):[block],
        schema.Optional('guidebook_page_whitelist'):[block],
        schema.Optional('weldall',default = True):flag,
        schema.Optional('needs_passive'):research,
        schema.Optional('research_requirement_override'):research,
        schema.Optional('entity'):{
            'type':str,
            'position':schema.Use(handlepos)
        },
        schema.Optional('guidebook_use_only',default = False):flag,
        schema.Optional('match_filter_modulo'):num, # flag?
    }],
    'summonore_pill':[{'filter':blocktag}],
    'sensor_natural':[{'filter':blocktag}],
    'sensor_rare_resource':[{'filter':blocktag}],
})

data2=dataschema.validate(data)

with open('data.json','w') as f:
    json.dump(data2,f,indent = 2)