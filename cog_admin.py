import glob
import nextcord
from nextcord.ext import commands
from lang import cmds
from commanddec import command2

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_permissions(administrator=True)
    command2("viewcog",classname="viewcog")
    async def viewcog(self, ctx):
        embed = nextcord.Embed()
        embed.description = ""
        for cog_name in glob.glob("cog_*.py"):
            embed.description += "| %s \n" % cog_name[:-3]
        await ctx.send(embed=embed)@commands.has_permissions(administrator=True)
    command2("viewcog",classname="viewcog")
    async def viewcog(ctx):
        embed = nextcord.Embed()
        embed.description = ""
        for cog_name in glob.glob("cog_*.py"):
            print([dir(o) for i, o in bot.cogs.items()])
            print([o.__cog_name__ for i, o in bot.cogs.items()])
            embed.description += "| %s \n" % cog_name[:-3]
        await ctx.send(embed=embed)
    @commands.has_permissions(administrator=True)
    command2("cog_load",classname="loadcog")
    async def loadcog(ctx, tar):
        try:
            bot.load_extension("cog_"+tar)
            await ctx.send("LOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("cog_"+tar+".py is already loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
            
    @commands.has_permissions(administrator=True)
    command2("cog_unload",classname="unloadcog")
    async def unloadcog(ctx, tar):
        try:
            if tar == "cog_admin": raise commands.errors.ExtensionNotFound # prevent softlock
            bot.unload_extension("cog_"+tar)
            await ctx.send("UNLOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("cog_"+tar+".py is already unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
            
    @commands.has_permissions(administrator=True)
    command2("cog_reload",classname="reloadcog")
    async def unloadcog(ctx, tar):
        try:
            bot.unload_extension("cog_"+tar)
            await ctx.send("RELOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")    
    
def setup(bot):
	bot.add_cog(Admin(bot))