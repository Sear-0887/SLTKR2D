import datetime
import decorator
import sys
from lang import cmdi
from colorama import Fore, init
from nextcord.ext import commands

init() # colorama's init(), not assetload's
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET


async def ErrorHandler(name, ctx, e, args, kwargs):
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
    expecterr = cmdi[name]["error"]
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
ctx = {ctx},
args = {args},
kwargs = {kwargs} 

{GREEN}Expected Error: "{expecterr}"
{RESET}{'-'*20}
'''
    )
    await ctx.send(expecterr)
    # raise e

def MainCommand(bot,name):
    # bot command
    cmdclass = cmdi[name]
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd) # decorator preserves the signature of cmd
    def fixcmd(cmd):
        print(cmdclass["aliases"])
        return bot.command(name=name, description=cmdclass["desc"], aliases=cmdclass["aliases"])(trycmd(cmd))
    return fixcmd

def CogCommand(name):
    # cog command
    # command gets a self argument as well
    cmdclass = cmdi[name]
    async def _trycmd(cmd,self,ctx,*args,**kwargs):
        try:
            await cmd(self,ctx,*args,**kwargs)
        except Exception as e:
            await ErrorHandler(name, ctx, e, args, kwargs)
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(name=name, description=cmdclass["desc"], aliases=cmdclass["aliases"])(trycmd(cmd))
    return fixcmd