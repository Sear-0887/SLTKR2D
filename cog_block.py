from assetload import blockinfos, quickidtable, frs
import nextcord
import random
import re
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import block_extra as be

class Block(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="block", description=cmd.block.desc, aliases=cmd.block.alias)
    async def block(self, ctx, blk=None):
        if blk:
            for key, ite in blockinfos.items():
                try: str(ite["id"])
                except: break
                val = str(ite["id"])
                if blk == key or blk == val:
                    embed = nextcord.Embed()
                    
                    img = Image.open("assets/block_zoo.png")
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
            await self.block(ctx, str(random.randint(0, 101)))

    
        
    @commands.command(name="image", description=cmd.image.desc, aliases=cmd.image.alias)
    #eswn
    async def image(self, ctx, dt="[[16][20]][[16][16]]"):
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
            print("BLOCKPATH = assets/textures/blocks/"+blockinfos[name]["path"])
            src = Image.open("assets/textures/blocks/"+blockinfos[name]["path"]).convert("RGBA")
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
        
def setup(bot):
	bot.add_cog(Block(bot))