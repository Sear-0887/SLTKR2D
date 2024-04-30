import datetime
import decorator
import json
import asyncio
import nextcord
from pyfunc.lang import cfg, evl
from colorama import Fore, init
from nextcord.ext import commands
import traceback
import logging 
init() # colorama's init(), not assetload's
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET
l = logging.getLogger()

async def ErrorHandler(name, e, args, kwargs, interaction=None, ctx=None):
    ctxorintr = ctx or interaction
    async def sendtoch(msg):
        if isinstance(ctxorintr, commands.Context):
            await ctx.send(msg)
        elif isinstance(ctxorintr, nextcord.Interaction):
            await interaction.response.send_message(msg)
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
    expecterr = evl(f"{name}.error")
    errortype = repr(type(e)).split("\'")[1] # <class '[KeyError]'>
    replacingerror = evl(f"{name}.error.{errortype}")
    if replacingerror:
        l.info(f"Other Error Message found for {name}: {replacingerror}")
        expecterr = replacingerror
    assert isinstance(expecterr,str)
    try:
        l.debug(f"{e.args=}")
        eargs = e.args[0]
        l.info(eargs)
        if isinstance(eargs, str):
            expecterr = expecterr.format(*args, e=eargs, **kwargs)
        elif isinstance(eargs, list):
            expecterr = expecterr.format(*args, *eargs, **kwargs)
        elif type(eargs) == dict:
            expecterr = expecterr.format(*args, **eargs, **kwargs)
    except Exception as EX:
        l.error(f"Unknown Error Happened when tring to replace keyword: {EX}")
        pass
    l.error(
f'''
{'-'*20}
{RED}Exception: " {BLUE}{e} {RED}"
{RED}on {name} ({type(e)}).

{BLUE}Passed Parameters:
{ctx = },
{interaction = }
{args = },
{kwargs = }

{GREEN}Expected Error: "{expecterr}"
{RESET}{'-'*20}
'''
    )
    await sendtoch(expecterr)
    guild = ctx.guild if ctxorintr == ctx else interaction.guild
    author = ctx.author if ctxorintr == ctx else interaction.user
    trigger = ctx.message.clean_content if ctxorintr == ctx else "<INTERACTION>"
    errorpacket = {
        "user": {
            "displayname": author.display_name,
            "globalname": author.global_name,
            'id': author.id,
            "servername": guild.name
        },
        'time': datetime.datetime.now().isoformat(),
        'trigger': trigger,
        'arg': [repr(a) for a in args],
        'kwarg': {k:repr(v) for k,v in kwargs.items()},
        'errline': '\n'.join(traceback.format_exception(e)),
        'errname': str(type(e)),
    }
    excstrs = [str(e)]
    while e.__context__ or e.__cause__:
        e = e.__context__ or e.__cause__
        excstrs = [str(e),*excstrs]
    errorpacket['excstr'] = '\n'.join(excstrs)
    
    errfilname = f"cache/log/error-{author.global_name}-{datetime.date.today():%d-%m-%Y}.json"
    try:
        with open(errfilname, "r") as fil:
            prev = json.load(fil)
    except:
        prev = []
    prev.append(errorpacket)
    with open(errfilname, "w") as fil:
        json.dump(prev, fil, indent=4)

def MainCommand(bot,name):
    # bot command
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await ctx.trigger_typing()
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd) # decorator preserves the signature of cmd
    def fixcmd(cmd):
        return bot.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name):
    # cog command
    # command gets a self argument as well
    async def _trycmd(cmd, self, ctx:commands.Context ,*args,**kwargs):
        try:
            await ctx.trigger_typing()
            await cmd(self, ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def InteractionCogCommand_Local(name):
    # interaction cog command
    # command gets a self argument as well
    async def _trycmd(cmd, self, interaction: nextcord.Interaction ,*args,**kwargs):
        try:
            await cmd(self, interaction, *args,**kwargs)
            
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, interaction=interaction)
            return
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return nextcord.slash_command(
            name        = name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            guild_ids   = cfg("botInfo.localICCServer")
        )( trycmd(cmd) )
    return fixcmd
