import datetime
import decorator
import json
import asyncio
import nextcord
from pyfunc.lang import cfg, evl
from colorama import Fore, init
from nextcord.ext import commands
import nextcord
import traceback
import logging 
import typing
init() # colorama's init(), not assetload's
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET
l = logging.getLogger()

Context:typing.TypeAlias = commands.context.Context

async def ErrorHandler(name:str, e:BaseException, args:tuple[typing.Any], kwargs:dict[str,typing.Any], interaction:nextcord.Interaction | None=None, ctx:Context | None=None) -> None:
    async def sendtoch(msg:str) -> None:
        if ctx is not None:
            await ctx.send(msg)
        elif interaction is not None:
            await interaction.response.send_message(msg)
        else:
            logging.error("something terrible has occurred! there's neither a context nor an interaction!")
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
    author:nextcord.user.User | nextcord.member.Member | None
    if ctx is not None:
        guild = ctx.guild
        author = ctx.author
        trigger = ctx.message.clean_content
    elif interaction is not None:
        guild = interaction.guild
        author = interaction.user
        trigger = "<INTERACTION>"
    else:
        guild = None
        author = None
        trigger = "<NONE!!!>"
        logging.error("something terrible has occurred! there's neither a context nor an interaction!")

    if author is not None:
        author_display_name = author.display_name
        author_global_name = author.global_name
        author_id = author.id
    else:
        author_display_name = '<NO AUTHOR>'
        author_global_name = '<NO AUTHOR>'
        author_id = 0

    if guild is not None:
        guild_name = guild.name
    else:
        guild_name = '<NO GUILD>'

    errorpacket = {
        "user": {
            "displayname": author_display_name,
            "globalname": author_global_name,
            'id': author_id,
            "servername": guild_name
        },
        'time': datetime.datetime.now().isoformat(),
        'trigger': trigger,
        'arg': [repr(a) for a in args],
        'kwarg': {k:repr(v) for k,v in kwargs.items()},
        'errline': '\n'.join(traceback.format_exception(e)),
        'errname': str(type(e)),
    }
    excstrs = [str(e)]
    while (e.__context__ or e.__cause__) is not None:
        e2 = e.__context__ or e.__cause__
        assert e2 is not None # seriously?
        e = e2
        excstrs = [str(e),*excstrs]
    errorpacket['excstr'] = '\n'.join(excstrs)
    
    errfilname = f"cache/log/error-{author_global_name}-{datetime.date.today():%d-%m-%Y}.json"
    try:
        with open(errfilname, "r") as fil:
            prev = json.load(fil)
    except:
        prev = []
    prev.append(errorpacket)
    with open(errfilname, "w") as fil:
        json.dump(prev, fil, indent=4)

CmdType:typing.TypeAlias = typing.Callable[...,typing.Coroutine]
NCmdType:typing.TypeAlias = commands.core.Command

def MainCommand(bot:nextcord.Bot,name:str) -> typing.Callable[[CmdType],NCmdType]:
    # bot command
    async def _trycmd(cmd:CmdType,ctx:commands.Context,*args:typing.Any,**kwargs:typing.Any) -> None:
        try:
            await ctx.trigger_typing()
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd:CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd) # decorator preserves the signature of cmd
    def fixcmd(cmd:CmdType) -> NCmdType:
        return bot.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name:str) -> typing.Callable[[CmdType],NCmdType]:
    # cog command
    # command gets a self argument as well
    async def _trycmd(cmd:CmdType, self:commands.Cog, ctx:commands.Context ,*args:typing.Any,**kwargs:typing.Any) -> None:
        try:
            await ctx.trigger_typing()
            await cmd(self, ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd:CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd:CmdType) -> NCmdType:
        return commands.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def InteractionCogCommand_Local(name:str) -> typing.Callable[[CmdType],NCmdType]:
    # interaction cog command
    # command gets a self argument as well
    async def _trycmd(cmd:CmdType, self:commands.Cog, interaction: nextcord.Interaction ,*args:typing.Any,**kwargs:typing.Any) -> None:
        try:
            await cmd(self, interaction, *args,**kwargs)
            
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, interaction=interaction)
            return
    def trycmd(cmd:CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd:CmdType) -> NCmdType:
        guild_ids = cfg("botInfo.localICCServer")
        assert isinstance(guild_ids,list)
        desc = evl(f"{name}.desc") or "*No Description.*"
        assert isinstance(desc,str)
        return nextcord.slash_command(
            name        = name,
            description = desc,
            guild_ids   = guild_ids
        )( trycmd(cmd) )
    return fixcmd
