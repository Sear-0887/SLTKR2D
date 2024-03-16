import glob
import os
import nextcord
from nextcord.ext import commands
from pyfunc.lang import evl
from pyfunc.commanddec import CogCommand
import datetime

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @CogCommand("viewcog")
    async def viewcog(self,ctx):
        embed = nextcord.Embed()
        embed.description = ""
        for cogname, cogins in self.bot.cogs.items():
            embed.description += f"### {cogname} (*{cogins.__class__.__module__}.py*) \n"
            for command in cogins.walk_commands():
                embed.description += f"‖ {command} \n"
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @CogCommand("loadcog")
    async def loadcog(self,ctx, tar):
        try:
            self.bot.load_extension("cog_"+tar)
            await ctx.send("LOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.send("cog_"+tar+".py is already loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")
            
    @commands.has_permissions(administrator=True)
    @CogCommand("unloadcog")
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
    @CogCommand("reloadcog")
    async def reloadcog(self,ctx, tar):
        try:
            self.bot.unload_extension("cog_"+tar)
            self.bot.load_extension("cog_"+tar)
            await ctx.send("RELOADED "+"cog_"+tar+".py")
        except commands.errors.ExtensionNotFound:
            await ctx.send("cog_"+tar+".py not found.")    
    
    @commands.has_permissions(administrator=True)
    @CogCommand("deletelog")
    async def delog(self, ctx):
        for cachef in glob.glob("cache/log/cache-??-??-????.txt"):
            os.remove(cachef)
        await ctx.send("Done.")
    
    @commands.has_permissions(administrator=True)
    @CogCommand("deleteerr")
    async def deleteerr(self, ctx):
        for errf in glob.glob("cache/log/error-*-??-??-????.txt"):
            os.remove(errf)
        await ctx.send("Done.")
    
    @CogCommand("viewerr")
    async def viewerr(self, ctx, user: nextcord.User=None):
        if user is None:
            username=ctx.author.global_name
        else:
            username=user.global_name
        for errf in glob.glob(f"cache/log/error-{username}-??-??-????.txt"):
            with open(errf) as f:
                parts=f.read().split('\n####:####\n')[:-1]
                for part in parts:
                    part=part.replace('`','ˋ') # nobody will notice
                    try:
                        await ctx.send('```\n'+part+'\n```')
                    except nextcord.errors.HTTPException: # the error was too long
                        part='\n'.join([x for x in part.split('\n') if not x.startswith('exctb-')])
                        try:
                            await ctx.send('```\n'+part+'\n```')
                        except nextcord.errors.HTTPException: # the error was still too long
                                await ctx.send('Error was too long.')

            
    
def setup(bot):
	bot.add_cog(Admin(bot))