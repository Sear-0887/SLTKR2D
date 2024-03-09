import datetime
import decorator
import sys
from pyfunc.lang import cmdi, evl
from colorama import Fore, init
from nextcord.ext import commands
import time
import traceback

init()
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET


async def ErrorHandler(name, ctx, e, args, kwargs):
    expecterr = evl(f"{name}.error")
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
    with open(f"cache/log/error-{ctx.author.global_name}-{datetime.date.today():%d-%m-%Y}.txt", "a+") as fil:
        userstr = f'user-:{ctx.author.display_name}\n'
        userstr += f'user-:{ctx.author.global_name}\n'
        userstr += f'user-:{ctx.author.id}'
        timestr = f'time-:{datetime.datetime.now().isoformat()}'
        cmdstr = '\n'.join([f'cmd-:{s}' for s in ctx.message.clean_content.split('\n')])
        argsstr = '\n'.join([f'arg-{i}:'+s for i,arg in enumerate(args) for s in repr(arg).split('\n')])
        kwargsstr = '\n'.join([k+':'+s for i,(k,v) in enumerate(kwargs.items()) for s in repr(v).split('\n')])
        exctbstr = '\n'.join(['exctb-:'+s for s in '\n'.join(traceback.format_exception(e)).split('\n')])
        excstr = '\n'.join([f'exc-:{s}' for s in str(e).split('\n')])
        fil.write('\n'.join([userstr,timestr,cmdstr,argsstr,kwargsstr,exctbstr,excstr]))
        fil.write('\n####:####\n') # record separator
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
        return bot.command(
            name        =        name, 
            description = evl(f"{name}.desc"), 
            aliases     = evl(f"{name}.aliases")
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name):
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

def CogGroup(name):
    cmdclass = cmdi[name]
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',ctx,args,kwargs)
            try:
                s=evl(f"{cmdclass}.error").format(*args,**kwargs)
            except:
                s=evl(f"{cmdclass}.error")
            await ctx.send(s)
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.group(
            name        =        name, 
            description = evl(f"{cmdclass}.desc"), 
            aliases     = evl(f"{cmdclass}.aliases")
        )( trycmd(cmd) )
    return fixcmd