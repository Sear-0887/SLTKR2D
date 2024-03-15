import datetime
import decorator
from pyfunc.lang import cmdi, evl
from colorama import Fore, init
from nextcord.ext import commands
import traceback

init() # colorama's init(), not assetload's
RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Fore.RESET


async def ErrorHandler(name, ctx, e, args, kwargs):
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
    expecterr = evl(name,"error")
    try:
        expecterr = expecterr.format(*args, **kwargs)
    except:
        pass
    print(
'''
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
            description = evl(name,"desc"), 
            aliases     = evl(name,"aliases")
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
            description = evl(name,"desc"), 
            aliases     = evl(name,"aliases")
        )( trycmd(cmd) )
    return fixcmd