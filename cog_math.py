import re
from nextcord.ext import commands
from commanddec import CogCommand
from eval_expr import evaluate,stringifyexpr

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @CogCommand("eval")
    async def evalu(self, ctx:commands.Context, *, formulae="3 * ( 1 + 2 )"):
        result=evaluate(formulae)
        await ctx.send(f"`{formulae} = {stringifyexpr(result)}`")
        
        
def setup(bot):
	bot.add_cog(Math(bot))