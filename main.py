import os
import nextcord
import keep_alive
import datetime
import random
import re
import decorator
from io import BytesIO
from PIL import Image
from nextcord.ext import commands
from lang import cmds, keywords

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmds.ping.desc)
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

def command(bot,name):
    async def _trycmd(cmd,*args,**kwargs):
        try:
            await cmd(*args,**kwargs)
        except Exception as e:
            print(e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return bot.command(name=name, description=getattr(cmds,name).desc, aliases=getattr(cmds,name).alias)(trycmd(cmd))
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
                desc = cmd.desc
                if cmdname == "link":
                    container = ""
                    for cr in keywords:
                        container += "%s (%s)\nKeywords: %s\n" % (cr, keywords[cr]["link"], ", ".join(keywords[cr]["kw"]))
                    desc = desc % container
                embed.title = cmdname
                embed.description = desc
                embed.add_field(name="Syntax", value=cmd.syntax)
                embed.add_field(name="Aliases", value=",\n".join(cmd.alias))
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
   
@command(bot,"block")
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
        await ctx.send(cmds.block.error % blk)
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
    
@command(bot,"image")
async def image(ctx, *, x="[[16][20]][[16][16]]"):
    blockp = [[False]*100 for _ in range(100)]
    width, height = 0, 0
    x.replace(" ", "")
    for y, row in enumerate(re.findall(r"\[(\[.*?\])\]+", x)):
        for x, block in enumerate(re.findall(r"\[([\w#]*)\]", row)):
            print(block, x, y)
            if block != "NIC" and block != "air":
                if block.isdigit():
                    block = quickidtable[int(block)]
                blockp[y][x] = block
                if block == "wire_board":
                    blockp[y][x] = "wafer,wire"
                elif block in "capacitor cascade counter diode galvanometer latch potentiometer transistor accelerometer matcher".split():
                    blockp[y][x] = "wafer,wire,#"+block
                elif block == "sensor":
                    blockp[y][x] = "wafer,wire,#sensor, sensor"
                elif block in "wire detector toggler trigger port":
                    blockp[y][x] = "frame,wire,#"+block
                elif block == "actuator":
                    blockp[y][x] = "#actuator_base,#actuator_head"
        else: 
            width = max(width, x) + 1
    else:
        height = max(height, y) + 1
    fin = Image.new("RGBA", (width*16, height*16))
    for y in range(height):
        for x in range(width):
            column = blockp[y][x]
            if column : #     e1,0   s0,1   w-1,0  n 0,-1
                print(column, (x, y))
                for fil in column.split(","):
                    flg = True
                    if fil.startswith("#"):
                        fil = fil[1:]
                        flg = not flg
                    print("textures/blocks/"+blockinfos[fil]["path"])
                    src = Image.open("textures/blocks/"+blockinfos[fil]["path"]).convert("RGBA")
                    cord = frs(blockp[y][x+1], blockp[y+1][x], blockp[y][x-1], blockp[y-1][x], src, flg)
                    # print(cord)
                    for e, crd in enumerate(cord):
                        fin.alpha_composite(src.crop(crd), (x*16+(e%2)*8, y*16+(e//2)*8))
    fin = fin.resize((width*16*2, height*16*2), Image.NEAREST)
    fin.save("f.png")
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
    
    
getblockid()
getblockpath()
getblockcord()
getlocal()
print(bot.all_commands["help"].description)
token = os.environ['token']
keep_alive.keep_alive()
bot.run(token)