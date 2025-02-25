import datetime
import decorator
import json
import asyncio
import nextcord
from pyfunc.lang import cfg, evl
from colorama import Fore, init as colorama_Init
from nextcord.ext import commands
import nextcord
import traceback
import logging 
import typing

colorama_Init()

RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET

l = logging.getLogger()

class User(typing.TypedDict):
    displayname: str
    globalname: str | None
    id: int
    servername: str

class ErrorPacket(typing.TypedDict):
    user: User
    time: str
    trigger: str
    arg: list[str]
    kwarg: dict[str,str]
    errline: str
    errname: str
    excstr: str

Context:typing.TypeAlias = commands.context.Context

async def ErrorHandler(
        name: str, 
        e: BaseException, 
        args: tuple[typing.Any], 
        kwargs: dict[str,typing.Any], 
        interaction: nextcord.Interaction | None=None, 
        ctx: Context | None = None
    ) -> None:
    async def sendToChannel(msg: str) -> None:
        if ctx is not None:
            await ctx.send(msg)
        elif interaction is not None:
            await interaction.response.send_message(msg)
        else:
            logging.error("Something terrible has occurred! there's neither a context nor an interaction!")
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
    errorMessage = evl(f"{name}.error")
    errorType = repr(type(e)).split("\'")[1] # <class '[KeyError]'>
    replacementErrorMsg = evl(f"{name}.error.{errorType}")
    if replacementErrorMsg:
        l.debug(f"Other Error Message found for {name}: {replacementErrorMsg}")
        errorMessage = replacementErrorMsg
    assert isinstance(errorMessage, str)
    try:
        l.debug(f"{e.args=}")
        errorArgs = e.args[0]
        if isinstance(errorArgs, str):
            errorMessage = errorMessage.format(*args, e=errorArgs, **kwargs)
        elif isinstance(errorArgs, list):
            errorMessage = errorMessage.format(*args, *errorArgs, **kwargs)
        elif type(errorArgs) == dict:
            errorMessage = errorMessage.format(*args, **errorArgs, **kwargs)
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

{GREEN}Expected Error: "{errorMessage}"
{RESET}{'-'*20}
'''
    )
    await sendToChannel(errorMessage)
    author: nextcord.user.User | nextcord.member.Member | None
    if ctx is not None:
        guild = ctx.guild
        author = ctx.author
        trigger = ctx.message.clean_content
    elif interaction is not None:
        guild = interaction.guild
        author = interaction.user
        trigger = (await interaction.original_message()).clean_content
    else:
        guild = None
        author = None
        trigger = "<NONE!!!>"
        # Duped Error

    if author is not None:
        author_display_name = author.display_name
        author_global_name = author.global_name
        author_id = author.id
    else:
        author_display_name = '<AUTHOR MISSING>'
        author_global_name = '<AUTHOR MISSING>'
        author_id = 0

    if guild is not None:
        guild_name = guild.name
    else:
        guild_name = '<GUILD MISSING>'

    excstrs = [str(e)]
    while (e.__context__ or e.__cause__) is not None:
        e2 = e.__context__ or e.__cause__
        assert e2 is not None # seriously mypy? eh.
        e = e2
        excstrs = [str(e),*excstrs]

    errorPacket: ErrorPacket = {
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
        'excstr': '\n'.join(excstrs),
    }
    
    errorLogFilename = f"cache/log/error-{author_global_name}-{datetime.date.today():%d-%m-%Y}.json"
    try:
        with open(errorLogFilename, "r") as fil:
            prevErrorPackets = json.load(fil)
    except:
        prevErrorPackets = []
    prevErrorPackets.append(errorPacket)
    with open(errorLogFilename, "w") as fil:
        json.dump(prevErrorPackets, fil, indent=4)

CmdType: typing.TypeAlias = typing.Callable[...,typing.Coroutine]
NCmdType: typing.TypeAlias = commands.core.Command

def MainCommand(bot: commands.Bot, name: str) -> typing.Callable[[CmdType],NCmdType]:
    # bot command
    async def _trycmd(cmd: CmdType, ctx: commands.Context, *args: typing.Any, **kwargs: typing.Any) -> None:
        try:
            await ctx.trigger_typing()
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd: CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd) # decorator preserves the signature of cmd
    def fixcmd(cmd: CmdType) -> NCmdType:
        return bot.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name: str) -> typing.Callable[[CmdType],NCmdType]:
    # cog command
    # command gets a self argument as well
    async def _trycmd(
            cmd: CmdType, 
            self: commands.Cog, 
            ctx: commands.Context,
            *args: typing.Any,
            **kwargs: typing.Any
        ) -> None:
        try:
            await ctx.trigger_typing()
            await cmd(self, ctx, *args, **kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, ctx=ctx)
    def trycmd(cmd: CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd: CmdType) -> NCmdType:
        return commands.command(
            name        =        name,
            description = evl(f"{name}.desc") or "*No Description Found.*",
            aliases     = evl(f"{name}.aliases") or []
        )( trycmd(cmd) )
    return fixcmd

def InteractionCogCommand_Local(name:str) -> typing.Callable[[CmdType],NCmdType]:
    # interaction cog command
    # command gets a self argument as well
    async def _trycmd(
        cmd: CmdType, 
        self: commands.Cog, 
        interaction: nextcord.Interaction,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        try:
            await cmd(self, interaction, *args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, e, args, kwargs, interaction=interaction)
            return
    def trycmd(cmd: CmdType) -> CmdType:
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd: CmdType) -> NCmdType:
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
