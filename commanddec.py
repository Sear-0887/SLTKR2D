import decorator
from lang import cmds
from nextcord.ext import commands

def command(bot,name):
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ctx.send(getattr(cmds,name).error % args)
            print(e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return bot.command(name=name, description=getattr(cmds,name).desc, aliases=getattr(cmds,name).aliases)(trycmd(cmd))
    return fixcmd

def command2(name,classname=None):
    if classname is None:
        classname=name
    cmdclass=getattr(cmds,classname)
    async def _trycmd(cmd,ctx,*args,**kwargs):
        try:
            await cmd(ctx,*args,**kwargs)
        except Exception as e:
            await ctx.send(cmdclass.error % args)
            print(e)
            raise e
    def trycmd(cmd):
        return decorator.decorate(cmd,_trycmd)
    def fixcmd(cmd):
        return commands.command(name=name, description=cmdclass.desc, aliases=cmdclass.aliases)(trycmd(cmd))
    return fixcmd