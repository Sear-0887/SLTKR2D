import decorator
from lang import cmdi, evl
from nextcord.ext import commands

def MainCommand(bot,name):
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',ctx,args,kwargs)
            try:
                s=evl(f"{name}.error").format(*args,**kwargs)
            except:
                s=evl(f"{name}.error")
            await ctx.send(s)
            print('the thing again:',e)
            raise e
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
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',ctx,args,kwargs)
            try:
                s=evl(f"{name}.error").format(*args,**kwargs)
            except:
                s=evl(f"{name}.error")
            await ctx.send(s)
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(
            name        =        name, 
            description = evl(f"{name}.desc"), 
            aliases     = evl(f"{name}.aliases")
        )( trycmd(cmd) )
    return fixcmd