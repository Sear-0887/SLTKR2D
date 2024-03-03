import datetime
import decorator
import sys
from lang import getcmdlocale
from colorama import Fore, init
from nextcord.ext import commands

init()
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET


async def ErrorHandler(name, ctx, e, args, kwargs):
    expecterr = getcmdlocale(f"{name}.error")
    try:
        expecterr = expecterr.format(*args, **kwargs)
    except:
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
    # raise e

def MainCommand(bot,name):
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        print(getcmdlocale(name,"aliases"))
        return bot.command(name=name, description=getcmdlocale(name,"desc"), aliases=getcmdlocale(name,"aliases"))(trycmd(cmd))
    return fixcmd

def CogCommand(name):
    async def _trycmd(cmd,self,ctx,*args,**kwargs):
        try:
            await cmd(self,ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(name=name, description=getcmdlocale(name,"desc"), aliases=getcmdlocale(name,"aliases"))(trycmd(cmd))
    return fixcmd