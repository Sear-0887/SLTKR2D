import glob
import nextcord
from nextcord.ext import commands
from lang import cmds

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_permissions(administrator=True)
    @commands.command(name="viewcog", description=cmds.viewcog.desc, aliases=cmds.viewcog.alias)
    async def viewcog(self, ctx):
        embed = nextcord.Embed()
        embed.description = ""
        for cog_name in glob.glob("cog_*.py"):
            embed.description += "| %s \n" % cog_name[:-3]
        await ctx.send(embed=embed)
    
def setup(bot):
	bot.add_cog(Admin(bot))