import collections
from pyfunc.assetload import blockinfos, idtoblock as quickidtable,locale
import nextcord
import random
import re
from PIL import Image
from nextcord.ext import commands
from pyfunc.lang import cfg
from pyfunc.commanddec import CogCommand
from pyfunc.assetload import idtoblock
from pyfunc.block import makeimage as blockmakeimage
import pyfunc.smp as smp

class Block(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @CogCommand("block")
    async def block(self,ctx, *, block=None):
        if block:
            if block.isdigit(): # if the argument is a number, get the corresponding block name
                block = idtoblock.get(int(block),'NIC')
            block = block.replace(" ", "_")
            binfo=blockinfos[block]
            embed = nextcord.Embed()
            pthblockzoo = cfg("localGame.texture.blockIconFile")
            img = Image.open(pthblockzoo)
            icox, icoy = binfo["iconcoord"]
            img = img.crop((16*icox, 16*icoy, 16*(icox+1), 16*(icoy+1))).resize((128, 128), Image.NEAREST)
            img.save("cache/blockim.png")
            embed.title = locale[("BLOCK_TITLE",block)]
            embed.add_field(name="Block name", value=block)
            embed.add_field(name="Block ID", value=binfo['id'])
            embed.add_field(name="Block Tutorial", value=locale[("BLOCK_TUTORIAL",block)])
            embed.set_image(url="attachment://blockim.png")

            await ctx.send(file=nextcord.File("cache/blockim.png", filename="blockim.png"), embed=embed)
        else:
            await self.block(ctx, str(random.choice([*idtoblock.keys()])))



    #eswn
    @CogCommand("image")
    async def image(self,ctx, *, x="[[16][20]][[16][16]]"):
        blocklist = collections.defaultdict(int)
        blocks=smp.getsmpvalue(x)
        for y,row in enumerate(blocks):
            for x,b in enumerate(row):
                print(b, x, y)
                b=b.lower().strip()
                b=''.join(b.split()) # remove all whitespace
                turn=0
                weld=[True,True,True,True]
                # either
                #   block          normal
                #   block#         normal
                #   block#dir      set facing
                #   block#weld     set welded sides
                #   block#dirweld  set both
                #   #block         no weld
                # welded sides is 4x 0 or 1 in the order right bottom left top
                # dir is eswn
                match=re.fullmatch('(?:([^]#]+)(?:#([eswn])?([01]{4})?)?)|#([^]]+)',b)
                if match is None:
                    raise Exception(f'Invalid block: {b}')
                b,turnm,weldm,unwelded=match.groups()
                if unwelded is not None:
                    weld=[False,False,False,False]
                    b=unwelded
                if turnm is not None:
                    turn='nwse'.index(turnm)
                if weldm is not None:
                    weld=[c=='1' for c in reversed(weldm)]
                if b=='nic': # nic is treated as air
                    b='air'
                if b.isdigit():
                    b = idtoblock[int(b)]
                blocks[y][x] = {"type":b,"rotate":turn,"weld":weld}
                blocklist[b] += 1
        im=blockmakeimage(blocks,32)
        im.save("cache/blocks.png")
        
        embed = nextcord.Embed()
        width, height = im.size
        embed.title = f"{width//32}x{height//32} Image"
        embed.set_image(url="attachment://f.png")
        
        embed.add_field(name="Material List", 
                        value=', '.join(
                            [f"{count} {block}"for block, count in blocklist.items()])
                        )
            
        await ctx.send(embed=embed, file=nextcord.File("cache/blocks.png", filename="f.png"))

def setup(bot):
	bot.add_cog(Block(bot))