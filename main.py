import os
import nextcord
import keep_alive
import datetime
import random
import re
import smp
from block import makeimage as blockmakeimage
from io import BytesIO
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmd.ping.desc)
quickidtable = ["NIC"]*102
blockinfos = defaultdict(dict)
def getblockid():
    with open("block_id_.smp") as f:
        data=smp.getsmpvalue(f.read())
    for name,i in data.items()
        blockinfos[name]["id"] = int(i)
        quickidtable[int(i)] = name

def getblockpath():
    with open("block_textures.smp") as f:
        data=smp.getsmpvalue(f.read())
    for name,texture in data.items()
        blockinfos[name]["path"] = texture

def getblockcord():
    with open("block_icons.smp") as f:
        data=smp.getsmpvalue(f.read())
    for icon,xy in data.items():
        x,y=xy.split(',')
        blockinfos[icon]["iconcord"] = (int(x), int(y))

def getlocal():
    for fnm in "blocks credits hud input menu misc tutorial".split():
        print(fnm)
        with open("localization/english_%s.txt" % fnm, "r") as f:
            fc = re.sub(r"\\\s*\n", r"\\", f.read())
            for line in fc.split("\n"):
                for a, n, v in re.findall(r"^(\w*?) (\w*)\s*=\s*(.*)", line):
                    try: blockinfos[n]
                    except: blockinfos[n] = {}
                    blockinfos[n][a] = v
    for blkkey, item in blockinfos.items():
        for blktype, txt in item.items():
            for tartype, tarname in re.findall("{(\w+) (\w+)}", str(txt)):
                if blockinfos[tarname]: 
                    if blockinfos[tarname][tartype]:
                        txt = re.sub("{%s %s}" % (tartype, tarname), blockinfos[tarname][tartype], txt)
                        blockinfos[blkkey][blktype] = txt
            for tartype, tarname, modifier in re.findall(r"{(\w+) (\w+)\|?([\^vsdbp]*)?}", str(txt)):
                if blockinfos[tarname]:
                    if blockinfos[tarname][tartype]:
                        tx = blockinfos[tarname][tartype]
                        for i in list(modifier):
                            if   i == "^": tx = tx[0].upper()+tx[1:]
                            elif i == "v": tx = tx[0].lower()+tx[1:]
                            elif i == "s": tx = tx + "s"
                            elif i == "d": tx = tx + "ed"
                            elif i == "p": tx = tx + "'s"
                            elif i == "b": tx = "{" + tx + "}"
                            txt = txt.replace("{%s %s|%s}" % (tartype, tarname, modifier), tx)
                        blockinfos[blkkey][blktype] = txt
    return blockinfos
    
@bot.command(name="help", description=cmd.help.desc, aliases=cmd.help.alias)
async def help(ctx, tcmd=None,):
    if not tcmd:
        embed = nextcord.Embed()
        embed.description = cmd.help.blankdisplay % (datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        async def gethelplist(interaction):
            sembed = nextcord.Embed()
            sembed.title = "Help List"
            sembed.description = "Here's a list of commands:\n" + ", ".join([func for func in dir(cmd) if not func.startswith("__")])
            await interaction.send(ephemeral=True, embed=sembed)
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn)
        await ctx.send(embed=embed, view=view)
    else:
        for i in bot.all_commands:
            if tcmd in bot.all_commands[i].aliases:
                tcmd = i
            if tcmd == i:
                embed = nextcord.Embed()
                clas = eval(f"cmd.{tcmd}")
                desc = clas.desc
                if tcmd == "link":
                    container = ""
                    for cr in keywords:
                        container += "%s (%s)\nKeywords: %s\n" % (cr, keywords[cr]["link"], ", ".join(keywords[cr]["kw"]))
                    desc = desc % container
                embed.title = tcmd
                embed.description = desc
                embed.add_field(name="Syntax", value=clas.syntax)
                embed.add_field(name="Aliases", value=",\n".join(clas.alias))
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(cmd.help.error)

@bot.command(name="ping", description=cmd.ping.desc, aliases=cmd.ping.alias)
async def ping(ctx):
    print(cmd.ping.cmddisplay % (bot.latency*1000))
    await ctx.send(cmd.ping.cmddisplay % (bot.latency*1000))
    
@bot.command(name="scream", description=cmd.scream.desc, aliases=cmd.scream.alias)
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
                icox, icoy = blockinfos[key]["iconcord"]
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

def frs(east, south, west, north, img, flg):
    wid, hei = img.size
    east = int(bool(east) and int(bool(east))*16 < wid and flg)*16
    south = int(bool(south) and int(bool(south))*16 < hei and flg)*16
    west = int(bool(west) and int(bool(west))*16 < wid and flg)*16
    north = int(bool(north) and int(bool(north))*16 < hei and flg)*16
    return ((west  , north  , west+8  , north+8  ),
            (east+8, north  , east+8+8, north+8  ),
            (west  , south+8, west+8  , south+8+8),
            (east+8, south+8, east+8+8, south+8+8))
    
@bot.command(name="image", description=cmd.image.desc, aliases=cmd.image.alias)
async def image(ctx, *, x="[[16][20]][[16][16]]"):
    blocks=smp.getsmpvalue(x)
    for y,row in enumerate(blocks):
        for x,b in enumerate(row):
            print(b, x, y)
            b=b.lower()
            if b=='nic':
                b='air'
            if b.isdigit():
                b = quickidtable[int(b)]
            blocks[y][x] = b
    im=blockmakeimage(blocks,32)
    im.save("f.png")
    await ctx.send(file=nextcord.File("f.png", filename="f.png"))
            

@bot.command(name="link", description=cmd.link.desc, aliases=cmd.link.alias)
async def link(ctx, typ="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(cmd.link.cmddisplay % (i, keywords[i]["link"]))
            return
    else:
        await ctx.send(cmd.link.error % typ)
        
@bot.event
async def on_ready():
    print("ONLINE as %s, id %s." % (bot.user, bot.user.id))
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now()
    
    
getblockid()
getblockpath()
getblockcord()
getlocal()
print(bot.all_commands["help"].description)
token = os.environ['token']
keep_alive.keep_alive()
bot.run(token)