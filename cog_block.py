from assetload import blockinfos, idtoblock as quickidtable,locale
import nextcord
import random
import re
from PIL import Image
from nextcord.ext import commands
from lang import cmds
import block_extra as be
from commanddec import command2
from assetload import idtoblock
from block import makeimage as blockmakeimage
import smp

class Block(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command2("block")
    async def block(self,ctx, block=None):
        if block:
            if block.isdigit():
                block = idtoblock.get(int(block),'NIC') # numeric id to string
            binfo=blockinfos[block]
            embed = nextcord.Embed()
            
            img = Image.open("assets/block_zoo.png")
            icox, icoy = binfo["iconcoord"]
            img = img.crop((16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))).resize((128, 128), Image.NEAREST)
            img.save("blockim.png")
            embed.title = locale[("BLOCK_TITLE",block)]
            embed.add_field(name="Block name", value=block)
            embed.add_field(name="Block ID", value=binfo['id'])
            embed.add_field(name="Block Tutorial", value=locale[("BLOCK_TUTORIAL",block)])
            embed.set_image(url="attachment://blockim.png")
            
            await ctx.send(file=nextcord.File("blockim.png", filename="blockim.png"), embed=embed)
        else:
            await self.block(ctx, str(random.choice([*idtoblock.keys()])))

    
        
    #eswn
    @command2("image")
    async def image(self,ctx, *, x="[[16][20]][[16][16]]"):
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
                    b = idtoblock[int(b)]
                blocks[y][x] = {"type":b,"rotate":turn,"weld":weld}
        im=blockmakeimage(blocks,32)
        im.save("blocks.png")
        await ctx.send(file=nextcord.File("blocks.png", filename="f.png"))
        
def setup(bot):
	bot.add_cog(Block(bot))