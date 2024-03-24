import collections
import glob
import itertools
from PIL import Image
import os
import random
from typing import Any
from pyfunc.lang import botinit, cfg
from pyfunc.smp import getsmpvalue
from pyfunc.block import makeimage
from pyfunc.assetload import blockinfos


botinit()
def massstrip(l:list):
    for i, j in enumerate(l):
        l[i] = j.strip()
    return l
def handletags(s:Any, organdict:dict) -> str | list:
    if not isinstance(s, str): return s 
    if s.startswith('$'):
        if s[1:] in organdict['tag'].keys():
            return organdict['tag'][s[1:]]
        print('Just a Normal name starts with $ ???????')
    return s

def handlegridtags(s:list, organdict:dict) -> tuple[list, str]:
    for y, xaxis in enumerate(s):
        for x, critem in enumerate(xaxis):
            s[y][x] = handletags(critem, organdict)
    return s


def addentries(i, entryname:str, typ:str, organdict:dict, includestr:str) -> list:
    includes = massstrip(includestr.split(','))
    entries = {}
    for key, item in i.items():
        item = handletags(item, organdict)
        if isinstance(item, str) and item.isdigit(): # Handle Numbers Differently
            item = int(item)
        if typ == 'heat' and key == 'needs_entity': # True for needs_entity
            item = bool(item)
        if typ == 'combine' and key == 'grid': # True for needs_entity
            item = handlegridtags(item, organdict)
        i[key] = item
        if key in includes:
            entries[key] = i[key]
    if entryname not in organdict[typ].keys():
        organdict[typ][entryname] = []
    organdict[typ][entryname].append(entries)
    
def every_recipe():
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
                producename = i['product'], 
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
                producename = i['product']['block']
                col = 'amount, grid'
            addentries(
                i, 
                producename, 
                "combine", 
                organdict, 
                col)
    return organdict

# Massive Comments Below to perform the Rubber duck debugging (https://en.wikipedia.org/wiki/Rubber_duck_debugging)
def generates(generated, recipenum, prodname, replacedhistroy=""):
    print(f"Generating | recipeframe-{prodname}-{replacedhistroy}.png") # Debug Purpose, Not removing in case
    for y, yaxis in enumerate(generated): # Open Grid
        for x, critem in enumerate(yaxis): # Scan through each block
            if critem == "NIC": critem = "air"
            if isinstance(critem, list): # If it's a list, it's a tag, which
                place = critem # Store the original list for the next iter to process
                for i in critem: # loops through tags element
                    generated[y][x] = {"type":i,"rotate":0,"weld":[True]*4,"data":None} # Modify the list element to be the block
                    generates(generated, recipenum, prodname, f"{replacedhistroy}~{i}") # Recursive, Passes the copy and informations to the sub process
                generated[y][x] = place # Places back the original list for the next iter to process
                return # Terminates the attempt because it cannot generate anything
            elif isinstance(critem, str): # It's normal and needed to NORMALIZE
                generated[y][x] = {"type":critem,"rotate":0,"weld":[True]*4,"data":None} # Actions
    else: 
        gen = makeimage(generated)
        gen = gen.resize((gen.size[0]*4, gen.size[1]*4), Image.NEAREST)
        gen.save(f"cache/recipeframe-{prodname}-{recipenum}{replacedhistroy}.png") # Save the final image

def generaterecipe(name):
    returned = every_recipe()
    for typ in returned.keys():
        if name in returned[typ]:
            print(f"{typ}: {returned[typ][name]}")
            gridpos = returned[typ][name]
            if typ == "combine":
                for num, entri in enumerate(gridpos):
                    generates(entri['grid'], num, name)
                    print()
                    gifcontainer: list[Image.Image] = []
                    for maderecipe in glob.glob(f"cache/recipeframe-{name}-*.png"):
                        gifcontainer.append(Image.open(maderecipe).convert("RGBA"))
                    gifcontainer[0].save(
                        f"cache/recipe-{name}.webp", 
                        format="webp",
                        save_all=True, 
                        append_images=gifcontainer[1:], 
                        duration=1000, 
                        loop=0, 
                        disposal=2)
                    for maderecipe in glob.glob(f"cache/recipeframe-{name}-*.png"):
                        try: os.remove(maderecipe)
                        except: pass
