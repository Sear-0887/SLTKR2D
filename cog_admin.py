import glob
import os
import nextcord
import json
from nextcord.ext import commands
from pyfunc.lang import evl
from pyfunc.commanddec import CogCommand
from collections import defaultdict
from itertools import takewhile,count
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
        for errf in glob.glob("cache/log/error-*-??-??-????.json"):
            os.remove(errf)
        await ctx.send("Done.")
    
    @CogCommand("viewerr")
    async def viewerr(self, ctx, count: int=1, user: nextcord.User=None, ):
        if count == "*": count = 999999 # All 
        if user is None: user = ctx.author
        async def senderr(values, filname):
            # Values
            user=values['user']
            time=values['time']
            cmd=values['trigger'].replace('`','ˋ')
            args=values['arg']
            kwargs=values['kwarg']
            exctb=values['errline'].replace('`','ˋ')
            exc=values['errname']
            excstr = values['excstr']
            # Embed
            embed = nextcord.Embed()
            embed.title = f'Error at {time}'
            desc = f"Caused by {user['displayname']} / {user['globalname']} \n"
            desc += f"<@{user['id']}> at {user['servername']} \n"
            desc += f"Command line: `{cmd}` \n"
            desc += f"Error Name: {exc} \n"
            desc += f"```{exctb}```"
            embed.description = desc
            for i,arg in enumerate(args):
                embed.add_field(name=f"Argument {i+1}", value=arg)
            for k,v in kwargs.items():
                embed.add_field(name=f"Kwarg {k}", value=v)
            embed.add_field(name=f"EXCSTR", value=excstr)
            if len(embed)>6000: # Error is too long
                desc = f"Caused by {user['displayname']} at {user['servername']} \n"
                desc += f"Command line: `{cmd}` \n"
                desc += f"Error Name: {exc} \n"
                desc += f"For more info, please view {filname}."
                embed.description = desc
            await ctx.send(embed=embed)
        
        errs=[]
        for fname in glob.glob(f"cache/log/error-{user.global_name}-??-??-????.json"):
            try:
                with open(fname) as f:
                    errs.extend([(fname,err) for err in json.load(f)])
            except: # not sure what kind of error to catch here
                pass
        if len(errs)==0:
            await ctx.send(f'No Error messages were found for {user.display_name}.')
        errs.sort(key=lambda x:datetime.datetime.fromisoformat(x[1]['time']))
        errs=[*reversed([*reversed(errs)][:count])]
        count = len(errs)
        print(f"printing {count} errors")
        for fname,err in errs:
            try:
                await senderr(err, fname)
            except nextcord.errors.HTTPException: # Error is STILL too long
                await ctx.send(f'The Error is too long to be displayed.\n Please view `{fname}` for more info.')

            
    
def setup(bot):
	bot.add_cog(Admin(bot))