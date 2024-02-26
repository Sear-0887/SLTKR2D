import glob
import nextcord
from nextcord.ext import commands
from commanddec import command2
import inspect
import json
import collections

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @command2("viewcog")
    async def viewcog(self,ctx):
        embed = nextcord.Embed()
        embed.description = ""
        data1={
            i:( # cog class name
                {
                    c.name:inspect.getfile(c._callback.__wrapped__) # command name and source file
                    for c in o.__cog_commands__ # for each command in a cog
                },
                inspect.getfile(o.__class__) # cog file
            )
            for i, o in self.bot.cogs.items() # for all cogs in the bot
        }
        data2=collections.defaultdict(dict)
        for cogclass,(cogdata,cogfile) in data1.items():
            data2[cogfile][cogclass]=[*cogdata.keys()]
        embed.description += json.dumps(data2,indent=2)+"\n"
        for cog_name in glob.glob("cog_*.py"):
            embed.description += f"| {cog_name[:-3]} \n"
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @command2("loadcog")
    async def loadcog(self,ctx, tar):
        try:
            self.bot.load_extension("cog_"+tar)
            await ctx.send("LOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("cog_"+tar+".py is already loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
            
    @commands.has_permissions(administrator=True)
    @command2("unloadcog")
    async def unloadcog(self,ctx, tar):
        try:
            if tar == "admin":
                await ctx.send("You can't unload cog_admin!") # prevent softlock
                return
            self.bot.unload_extension("cog_"+tar)
            await ctx.send("UNLOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("cog_"+tar+".py is already unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
            
    @commands.has_permissions(administrator=True)
    @command2("reloadcog")
    async def reloadcog(self,ctx, tar):
        try:
            self.bot.unload_extension("cog_"+tar)
            self.bot.load_extension("cog_"+tar)
            await ctx.send("RELOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
    
def setup(bot):
	bot.add_cog(Admin(bot))