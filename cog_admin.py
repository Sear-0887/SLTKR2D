import glob
from assetload import blockinfos, quickidtable, frs
import nextcord
import datetime
import random
import re
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import block_extra as be

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_permissions(administrator=True)
    @commands.command(name="viewcog", description=cmd.viewcog.desc, aliases=cmd.viewcog.alias)
    async def viewcog(self, ctx):
        embed = nextcord.Embed()
        embed.description = ""
        for cog_name in glob.glob("cog_*.py"):
            embed.description += "| %s \n" % cog_name[:-3]
        await ctx.send(embed=embed)
    
def setup(bot):
	bot.add_cog(Admin(bot))