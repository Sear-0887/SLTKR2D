import decorator
from lang import cmdi, evl
from nextcord.ext import commands

def MainCommand(bot,name):
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
        print(evl(f"{cmdclass}.aliases"))
        return bot.command(
            name        =        name, 
            description = evl(f"{cmdclass}.desc"), 
            aliases     = evl(f"{cmdclass}.aliases")
        )( trycmd(cmd) )
    return fixcmd

def CogCommand(name):
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
        return commands.command(
            name        =        name, 
            description = evl(f"{cmdclass}.desc"), 
            aliases     = evl(f"{cmdclass}.aliases")
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