import decorator
from lang import cmds
from nextcord.ext import commands

def command(bot,name,classname=None):
    if classname is None:
        classname=name
    cmdclass=getattr(cmds,classname)
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            await ctx.send(cmdclass.error.format(*args[1:]))
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return bot.command(name=name, description=cmdclass.desc, aliases=cmdclass.aliases)(trycmd(cmd))
    return fixcmd

def command2(name,classname=None):
    if classname is None:
        classname=name
    cmdclass=getattr(cmds,classname)
    async def _trycmd(cmd,self,ctx,*args,**kwargs):
        try:
            await cmd(ctx,self,*args,**kwargs)
        except Exception as e:
            print('the thing:',e,type(e))
            print('the thing:',self,ctx,args,kwargs)
            await ctx.send(cmdclass.error.format(*args[1:]))
            print('the thing again:',e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(name=name, description=cmdclass.desc, aliases=cmdclass.aliases)(trycmd(cmd))
    return fixcmd