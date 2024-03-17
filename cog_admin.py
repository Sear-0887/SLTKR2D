import glob
import os
import nextcord
from nextcord.ext import commands
from pyfunc.lang import evl
from pyfunc.commanddec import CogCommand
from collections import defaultdict
from itertools import takewhile,count


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
    async def viewerr(self, ctx, user: nextcord.User=None, count: int=5):
        if user is None:
            username=ctx.author.global_name
        else:
            username=user.global_name
        async def senderr(err):
            values=defaultdict(list)
            for line in err.split('\n'):
                if ':' not in line:
                    continue
                key,val=line.split(':',maxsplit=1)
                values[key].append(val)
            values={key:'\n'.join(val) for key,val in values.items()}
            user=values['user-']
            time=values['time-']
            cmd=values['cmd-'].replace('`','ˋ')
            args=[values[f'arg-{i}'] for i in takewhile(lambda i:f'arg-{i}' in values,count())]
            exctb=values['exctb-'].replace('`','ˋ')
            exc=values['exc-']
            kwargs={k:v for k,v in values.items() if '-' not in k} # assuming here that - isn't allowed in kwargs
            embed = nextcord.Embed()
            embed.title = f'Error at {time}'
            embed.description = f'Caused by {user}\nCommand line: `{cmd}`\nTraceback: ```{exctb}```'
            for i,arg in enumerate(args):
                embed.add_field(name=f"Argument {i+1}", value=arg)
            for k,v in kwargs.items():
                embed.add_field(name=f"Kwarg {k}", value=v)
            if len(embed)>6000:
                embed.description = f'Caused by {user}\nCommand line: `{cmd}`\nError message: ```{exc}```'
            await ctx.send(embed=embed)
        for errf in glob.glob(f"cache/log/error-{username}-??-??-????.txt"):
            parts=[]
            with open(errf) as f:
                parts+=f.read().split('\n####:####\n')[:-1]
            partdates=[
                (
                    datetime.datetime.fromisoformat([
                        line[6:] for line in part.split('\n')
                        if line.startswith('time-:')
                    ][0]),
                    part
                )
                for part in parts
            ]
            for date,part in sorted(partdates)[-count:]:
                part=part.replace('`','ˋ') # nobody will notice
                try:
                    await ctx.send('```\n'+part+'\n```')
                except nextcord.errors.HTTPException: # the error was too long
                    part='\n'.join([x for x in part.split('\n') if not x.startswith('exctb-')])
                    try:
                        await senderr(part)
                    except nextcord.errors.HTTPException: # the error was still too long
                        await ctx.send('Error was too long.')

            
    
def setup(bot):
	bot.add_cog(Admin(bot))