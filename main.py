import os
import nextcord
import datetime
import random
import re
import decorator
import smp
from block import makeimage as blockmakeimage
from io import BytesIO
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import collections

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmds.ping.desc)
idtoblock = {}

blockinfos = {}

locale={}

localedir='localization'
lang='english'

def capitalize(s):
    s=s[0].upper()+s[1:]
    return s

def plural(s):
    if s.endswith('y'): # just in case
        s=s[:-1]+'ie'
    s+="s"
    return s

def past(s):
    if s.endswith('e'):
        s=s[:-1]
    s+="ed"
    return s

modifiers={
    '^':capitalize,
    's':plural,
    'd':past,
}

def getblockids():
    with open("block_id_.smp") as f:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{([\d]*)\}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["id"] = int(i)
            idtoblock[int(i)] = n

def getblocktextures():
    with open("block_textures.smp") as f:
        pattern = re.compile(r"{(.*)}:{(.*)}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["path"] = i         

def getblockcoords():
    with open("block_icons.smp") as gbc:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{\s*([\d]*),\s*([\d]*)\}")
        for a, x, y in re.findall(pattern, gbc.read()):
            blockinfos[a]["iconcord"] = (int(x), int(y))

def substitutelocale(s):
    i=0 # the index to look for the next opening bracket at
    while '{' in s[i:]:
        i1=s.index('{',i)
        i2=s.find('}',i1)
        if i2==-1: # there is no closing bracket
            break
        p1=s[:i1]
        p2=s[i1+1:i2]
        p3=s[i2+1:]
        i=i1+1
        if '|' in p2:
            p2,modifier=p2.split('|',maxsplit=1)
        else:
            modifier=''
        key=tuple(part.strip() for part in p2.split())
        if key in locale:
            localized=locale[key]
            for mod in modifier:
                localized=modifiers[mod](localized)
            s=p1+localized+p3
    return s

def getlocale():
    for fname in os.listdir(localedir):
        if not fname.startswith(lang):
            continue # skip files for a different language
        with open(os.path.join(localedir,fname), "r") as f:
            linesiter=iter(f)
            for line in linesiter:
                while line.endswith('\\\n'):
                    line=line[:-1]+next(linesiter) # add the next line to this if this line ends with a backslash
                line=re.sub('#.*$','',line) # remove comments
                if '=' not in line:
                    continue
                key,value=line.split('=',maxsplit=1)
                key=tuple(key.split())
                value=value.strip()
                locale[key]=value

    for key,s in locale.items():
        locale[key]=substitutelocale(s)

def command(bot,name):
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ctx.send(getattr(cmds,name).error % args)
            print(e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return bot.command(name=name, description=getattr(cmds,name).desc, aliases=getattr(cmds,name).aliases)(trycmd(cmd))
    return fixcmd

@command(bot,"help")
async def help(ctx, cmdname=None,):
    if not cmdname:
        embed = nextcord.Embed()
        embed.description = cmds.help.blankdisplay % (datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        async def gethelplist(interaction):
            sembed = nextcord.Embed()
            sembed.title = "Help List"
            sembed.description = "Here's a list of commands:\n" + ", ".join([cmd for cmd in dir(cmds) if not cmd.startswith("__")])
            await interaction.send(ephemeral=True, embed=sembed)
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn)
        await ctx.send(embed=embed, view=view)
    else:
        for i in bot.all_commands:
            if cmdname in bot.all_commands[i].aliases:
                cmdname = i
            if cmdname == i:
                embed = nextcord.Embed()
                cmd = getattr(cmds,cmdname)
                embed.title = cmdname
                embed.description = cmd.desc
                embed.add_field(name="Syntax", value=cmd.syntax)
                embed.add_field(name="Aliases", value=",\n".join(cmd.aliases))
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(cmds.help.error)

@command(bot,"ping")
async def ping(ctx):
    s=f"Pong! ({bot.latency*1000} ms)"
    print(s)
    await ctx.send(s)
    
@command(bot,"scream")
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)
   
@bot.command(name="block", description=cmd.block.desc, aliases=cmd.block.alias)
async def block(ctx, blk=None):
    if blk:
        for key, ite in blockinfos.items():
            try: str(ite["id"])
            except: break
            val = str(ite["id"])
            if blk == key or blk == val:
                embed = nextcord.Embed()
                
                img = Image.open("block_zoo.png")
                icox, icoy = blockinfos[key]["iconcoord"]
                img = img.crop((16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))).resize((128, 128), Image.NEAREST)
                img.save("sed.png")
                embed.title = ite["BLOCK_TITLE"]
                embed.add_field(name="Block name", value=key)
                embed.add_field(name="Block ID", value=val)
                embed.add_field(name="Block Tutorial", value=re.sub(r"\\", r"\n", ite["BLOCK_TUTORIAL"]))
                embed.set_image(url="attachment://sed.png")
                
                await ctx.send(file=nextcord.File("sed.png", filename="sed.png"), embed=embed)
                return
        await ctx.send(cmd.block.error % blk)
    else:
        await block(ctx, str(random.randint(0, 101)))
    
@command(bot,"image")
async def image(ctx, *, x="[[16][20]][[16][16]]"):
    blocks=smp.getsmpvalue(x)
    for y,row in enumerate(blocks):
        for x,b in enumerate(row):
            print(b, x, y)
            b=b.lower()
            turn=0
            weld=[True,True,True,True]
            if '#' in b:
                b,weld=b.split('#',maxsplit=1)
                if weld[0] in 'eswn':
                    turn='nwse'.index(weld[0])
                    weld=weld[1:]
                assert len(weld)==4
                weld=[c=='1' for c in reversed(weld)]
            if b=='nic':
                b='air'
            if b.isdigit():
                b = quickidtable[int(b)]
            blocks[y][x] = {"type":b,"rotate":turn,"weld":weld}
    im=blockmakeimage(blocks,32)
    im.save("f.png")
    await ctx.send(file=nextcord.File("f.png", filename="f.png"))
            

@command(bot,"link")
async def link(ctx, typ="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(f"`{i}` - {keywords[i]['link']}")
            return
    else:
        await ctx.send(cmds.link.error % typ)
        
@bot.event
async def on_ready():
    print("ONLINE as %s, id %s." % (bot.user, bot.user.id))
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now()
    
    
getblockids()
geticoncoords()
getlocale()
print(bot.all_commands["help"].description)
token = os.environ['token']
bot.run(token)
