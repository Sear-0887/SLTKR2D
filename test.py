import pyfunc.smp as smp
import collections
import copy
import json

with open("gameAssets/recipes.smp") as f:
    rawdata = smp.getsmpvalue(f.read())

data=collections.defaultdict(list)

for x in rawdata:
    x=copy.deepcopy(x)
    typ=x['type']
    del x['type']
    data[typ].append(x)

print(json.dumps({dk:[*set([k for x in d for k in x.keys()])] for dk,d in data.items()},indent=2))

tags=collections.defaultdict(list)

for tag in data['tag']:
    tag=copy.deepcopy(tag)
    name=x['name']
    del x['name']
    tags[name].append(x['blocks'])

heat=collections.defaultdict(list)

for h in data['heat']:
    h=copy.deepcopy(h)
    if 'needs_entity' in h and h['needs_entity']=='1':
        h['needs_entity']=True
    heat[h['product']].append(h)

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
    extra_display[e['product']].append(e)

summonore_pill=collections.defaultdict(list)

for s in data['summonore_pill']: # there is literally only one
    s=copy.deepcopy(s)
    hmm
    summonore_pill[s['product']].append(s)

# filters:
# grassy
# non_air
# needs_collision
# buildable
# not_water
# needs_container_count5