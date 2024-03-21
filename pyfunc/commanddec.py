import datetime
import decorator
import json
from pyfunc.lang import cmdi, evl
from colorama import Fore, init
from nextcord.ext import commands
import traceback

init() # colorama's init(), not assetload's
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET

# User: {errorpacket['user']['displayname']}/{errorpacket['user']['globalname']}
# | (<@{errorpacket['user']['id']}> in Server {errorpacket['user']['servername']})
# At: {errorpacket['time']}'
# {errorpacket['trigger']}
# {errorpacket['arg']}
# {errorpacket['kwarg']}
# ExceptionName: " {errorpacket['errname']} "
# Detail:
# {errorpacket['errline']}
# Exc- {excstr}
async def ErrorHandler(name, ctx:commands.Context, e, args, kwargs):
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
    expecterr = evl(f"{name}.error")
    errortype = repr(type(e)).split("\'")[1] # <class '[KeyError]'>
    replacingerror = evl(f"{name}.error.{errortype}")
    if replacingerror:
        print(f"Other Error Message found for {name}: {replacingerror}")
        expecterr = replacingerror
    try:
        print(f"{e.args=}")
        eargs = e.args[0]
        print(eargs)
        if isinstance(eargs, str):
            expecterr = expecterr.format(*args, e=eargs, **kwargs)
        elif isinstance(eargs, list):
            expecterr = expecterr.format(*args, *eargs, **kwargs)
        elif type(eargs) == dict:
            expecterr = expecterr.format(*args, **eargs, **kwargs)
    except Exception as EX:
        print(EX)
        pass
    print(
f'''
{'-'*20}
{RED}Exception: " {BLUE}{e} {RED}"
{RED}on {name} ({type(e)}).

{BLUE}Passed Parameters:
{ctx = },
{args = },
{kwargs = }

{GREEN}Expected Error: "{expecterr}"
{RESET}{'-'*20}
'''
    )
    await ctx.send(expecterr)
    errorpacket = {
        "user": {
            "displayname": ctx.author.display_name,
            "globalname": ctx.author.global_name,
            'id': ctx.author.id,
            "servername": ctx.guild.name
        },
        'time': datetime.datetime.now().isoformat(),
        'trigger': ctx.message.clean_content,
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
    
    errfilname = f"cache/log/error-{ctx.author.global_name}-{datetime.date.today():%d-%m-%Y}.json"
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
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd) # decorator preserves the signature of cmd
    def fixcmd(cmd):
        return bot.command(
            name        =        name,
            description = evl(f"{name}.desc"),
            aliases     = evl(f"{name}.aliases")
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name):
    # cog command
    # command gets a self argument as well
    async def _trycmd(cmd, self, ctx:commands.Context ,*args,**kwargs):
        try:
            await cmd(self, ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(
            name        =        name,
            description = evl(f"{name}.desc"),
            aliases     = evl(f"{name}.aliases")
        )( trycmd(cmd) )
    return fixcmd