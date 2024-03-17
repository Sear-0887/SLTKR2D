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
async def ErrorHandler(name, ctx:commands.Context, e:Exception, args, kwargs):
    # handle the error e
    # from a function call f(ctx,*args,**kwargs)
    # print a message with cool colors to the console
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
    errorpacket = {}
    errorpacket['user'] = {
        "displayname": ctx.author.display_name,
        "globalname": ctx.author.global_name,
        'id': ctx.author.id,
        "servername": ctx.guild.name
    }
    errorpacket['time'] = datetime.datetime.now().isoformat()
    errorpacket['trigger'] = ctx.message.clean_content.split('\n')
    errorpacket['arg'] = args
    errorpacket['kwarg'] = kwargs
    errorpacket['errname'] = str(e).split('\n')
    errorpacket['errline'] = '\n'.join(traceback.format_exception(e)).split("\n")
    excstr = ""
    while e.__context__ or e.__cause__:
        e = e.__context__ or e.__cause__
        excstr = '\n'.join([f'exc-:{s}' for s in str(e).split('\n')]) + excstr
    errorpacket['excstr'] = excstr
    
    errfilname = f"cache/log/error-{ctx.author.global_name}-{datetime.date.today():%d-%m-%Y}.json"
    with open(errfilname, "r") as fil:
        prev = []
        try:
            prev = json.load(fil)
        except: pass
    prev.append(errorpacket)
    with open(errfilname, "w+") as fil:
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