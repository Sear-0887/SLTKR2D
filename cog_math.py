import re
from nextcord.ext import commands
from commanddec import CogCommand
from eval_expr import evaluate,NUM

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @CogCommand("eval")
    async def evalu(self, ctx:commands.Context, *, formulae="3 * ( 1 + 2 )"):
        result=evaluate(formulae)
        if result[0]!=NUM:
            raise Exception('didn\'t output a number')
        await ctx.send(f"{formulae} = {result[1]}")
        
        
def setup(bot):
	bot.add_cog(Math(bot))