import decorator
from lang import cmdi
from nextcord.ext import commands

def command(bot,name):
    cmdclass = cmdi[name]
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',ctx,args,kwargs)
            try:
                s=cmdclass["error"].format(*args,**kwargs)
            except:
                s=cmdclass["error"]
            await ctx.send(s)
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        print(cmdclass["aliases"])
        return bot.command(name=name, description=cmdclass["desc"], aliases=cmdclass["aliases"])(trycmd(cmd))
    return fixcmd

def command2(name):
    cmdclass = cmdi[name]
    async def _trycmd(cmd,self,ctx,*args,**kwargs):
        try:
            await cmd(self,ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',self,ctx,args,kwargs)
            try:
                s=cmdclass["error"].format(*args,**kwargs)
            except:
                s=cmdclass["error"]
            await ctx.send(s)
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(name=name, description=cmdclass["desc"], aliases=cmdclass["aliases"])(trycmd(cmd))
    return fixcmd