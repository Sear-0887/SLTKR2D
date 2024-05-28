import collections
import glob
from pyfunc.assetload import blockinfos, idtoblock, locale
import nextcord
import random
import re
from PIL import Image
from nextcord.ext import commands
from pyfunc.lang import cfgstr
from pyfunc.commanddec import CogCommand
from pyfunc.block import makeimage as blockmakeimage, BlockDataIn
import pyfunc.smp as smp
from pyfunc.recipe import generaterecipe
import typing

class Block(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @CogCommand("block")
    async def block(self,ctx:commands.Context, *, block:str | None=None) -> None:
        if block is not None:
            if block.isdigit(): # if the argument is a number, get the corresponding block name
                block = idtoblock.get(int(block),'NIC')
            block = block.replace(" ", "_")
            binfo=blockinfos[block]
            embed = nextcord.Embed()
            pthblockzoo = cfgstr("localGame.texture.blockIconFile")
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

    @CogCommand("image")
    async def image(self,ctx:commands.Context, *, build:str="[[16][20]][[16][16]]") -> None:
        blocklist:dict[str, int] = collections.defaultdict(int)
        blocks:list[list[BlockDataIn]]=typing.cast(list[list[BlockDataIn]],smp.getsmpvalue(build))
        for y,row in enumerate(blocks):
            for x,b in enumerate(row):
                assert isinstance(b,str)
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
                # all block can have :data after it
                # data is block specific
                match=re.fullmatch('(?:(?:([^]#:]+)(?:#([eswn])?([01]{4})?)?)|#([^]]+))(?::([^]]+))?',b)
                if match is None:
                    raise Exception(f'Invalid block: {b}')
                b,turnm,weldm,unwelded,bdata=match.groups()
                if unwelded is not None:
                    weld=[False,False,False,False]
                    b=unwelded
                if turnm is not None:
                    turn='nwse'.index(turnm)
                if weldm is not None:
                    weld=[c=='1' for c in reversed(weldm)]
                if b.isdigit():
                    b = idtoblock[int(b)]
                blocks[y][x] = typing.cast(BlockDataIn,{"type":b,"rotate":turn,"weld":weld,"data":bdata}) # just assume
                blocklist[b] += 1
        im=blockmakeimage(blocks)
        width, height = im.size
        im=im.resize((width*4,height*4),Image.NEAREST) # 16x16 to 128x128
        im.save("cache/blocks.png")
        
        embed = nextcord.Embed()
        embed.title = f"{width//16}x{height//16} Image"
        embed.set_image(url="attachment://f.png")
        iterdic = dict(sorted(blocklist.items(), key=lambda item: item[1], reverse=True))
        materialist = ', '.join([f"{count} {block}" for block, count in iterdic.items()])
        if len(materialist) <= 1024:
            embed.add_field(name="Material List", value=materialist)
            await ctx.send(embed=embed, file=nextcord.File("cache/blocks.png", filename="f.png"))
        else:
            with open("cache/materialist.txt", "w") as f:
                f.write(materialist.replace(", ", ", \n"))
            embed.add_field(name="Material List", value="*Please Refer to `material_list.txt` for the material list.*")
            await ctx.send(
                embed=embed, 
                files=[
                    nextcord.File("cache/blocks.png", filename="f.png"),
                    nextcord.File("cache/materialist.txt", filename="material_list.txt")
                ]
            )
            
    @CogCommand("recipe")
    async def recipe(self,ctx:commands.Context, *, block:str='extractor') -> None:
        if block.isdigit(): # if the argument is a number, get the corresponding block name
            block = idtoblock.get(int(block),'NIC')
        block = block.replace(" ", "_").lower()
        generaterecipe(block)
        embed = nextcord.Embed()
        embed.title = f"{block}'s Recipe"
        embed.set_image(url="attachment://f.gif")
        await ctx.send(embed=embed, file=nextcord.File(f"cache/recipe-{block}.gif", filename="f.gif"))  
        
        
def setup(bot:commands.Bot) -> None:
	bot.add_cog(Block(bot))
