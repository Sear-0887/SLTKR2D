import os
import nextcord
import keep_alive
import datetime
import random
import re
from io import BytesIO
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import block_extra as be

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmd.ping.desc)
quickidtable = ["NIC"]*102
blockinfos = {}
def getblockid():
    with open("block_id_.smp") as f:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{([\d]*)\}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["id"] = int(i)
            quickidtable[int(i)] = n

def getblockpath():
    with open("block_textures.smp") as f:
        pattern = re.compile(r"{(.*)}:{(.*)}")
        for n, i in re.findall(pattern, f.read()):
            try: blockinfos[n]
            except: blockinfos[n] = {}
            blockinfos[n]["path"] = i         

def getblockcord():
    with open("block_icons.smp") as gbc:
        pattern = re.compile(r"\{([a-zA-Z_]*)\}\s*:\s*\{\s*([\d]*),\s*([\d]*)\}")
        for a, x, y in re.findall(pattern, gbc.read()):
            blockinfos[a]["iconcord"] = (int(x), int(y))
    return False

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

def frs(east, south, west, north, wt, flg):
    wt = int(wt, 2)
    info = int(east)*8+int(south)*4+int(west)*2+int(north)
    print(info, east, south, west, north, flg, wt)
    info = info & wt & flg 
    print(str(bin(info))[2:].zfill(4))
    info = list(str(bin(info))[2:].zfill(4))
    print(flg, info)
    east = int(east and info[0])*16
    south = int(south and info[1])*16
    west = int(west and info[2])*16
    north = int(north and info[3])*16
    return ((west  , north  , west+8  , north+8  ),
            (east+8, north  , east+8+8, north+8  ),
            (west  , south+8, west+8  , south+8+8),
            (east+8, south+8, east+8+8, south+8+8))
    
@bot.command(name="image", description=cmd.image.desc, aliases=cmd.image.alias)
#eswn
async def image(ctx, dt="[[16][20]][[16][16]]"):
    blockp = []#3layer
    cordic = []
    cordwr = []
    width, height = 0, 0 
    dt.replace(" ", "")
    dt = dt.lower()
    for y, row in enumerate(re.findall(r"\[(\[.*?\])\]+", dt)):
        for x, raw in enumerate(re.findall(r"\[([\w]+)#?([\d]{4}|)#?([\d]{1}|)\]", row)):
            block, weldtag, rotation = raw
            if not weldtag: weldtag = "1111"
            if block.isdigit():
                block = quickidtable[int(block)]
                print(block, weldtag, rotation, x, y)
            if block != "NIC" and block != "air":
                if block in be.wiredtypes:
                    if block in be.wafertypes:
                        blockp += [("wafer", weldtag, x, y),
                                    (block, "0000", x, y)]
                        blockp += [("wire", weldtag, x, y)]
                    if block in be.frametypes:
                        blockp += [("frame", weldtag, x, y), 
                                    (block, "0000", x, y)]
                        blockp += [("wire", weldtag, x, y)]
                    if block == "actuator":
                        blockp += [("actuator_base", "0001", x, y), 
                                ("actuator_head", "1111", x, y)]
                    cordwr += [(x,y)]
                    
                else:
                    blockp += [(block, weldtag, x, y)]
                    print("T")
            cordic += [(x, y)]
        width = max(width, x+1)
    height = max(height, y+1)
    print("WIDTH, HEIGHT =", width, height)
    fin = Image.new("RGBA", (width*16, height*16))
    print(blockp)
    for name, wt, x, y in blockp:#     e1,0   s0,1   w-1,0  n 0,-1 
        print("")
        print("name,wt,(x,y)", name, wt, (x, y))
        print("BLOCKPATH = textures/blocks/"+blockinfos[name]["path"])
        src = Image.open("textures/blocks/"+blockinfos[name]["path"]).convert("RGBA")
        spflg = "1111"
        findcord = cordwr if name == "wire" else cordic
        for i, j in be.weldspr.items():
            if name in j: 
                spflg = i
        
        cord = frs(
            (x+1, y) in findcord, 
            (x, y+1) in findcord, 
            (x-1, y) in findcord, 
            (x, y-1) in findcord, 
            wt,
            int(spflg, 2))
        print(cord, spflg)
        for e, crd in enumerate(cord):
            fin.alpha_composite(src.crop(crd), (x*16+(e%2)*8, y*16+(e//2)*8))
    fin = fin.resize((width*16*2, height*16*2), Image.NEAREST)
    fin.save("f.png")
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