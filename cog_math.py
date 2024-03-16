import matplotlib.pyplot as plt
import numpy
import nextcord
import math
from pyfunc.math import primefactor
from nextcord.ext import commands
from pyfunc.commanddec import CogCommand
from pyfunc.eval_expr import evaluate,stringifyexpr

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @CogCommand("eval")
    async def eval(self, ctx:commands.Context, *, formulae="3 * ( 1 + 2 )"):
        result=evaluate(formulae)
        await ctx.send(f"`{formulae} = {stringifyexpr(result)}`")
    
    @CogCommand("plot")
    async def plot(self, ctx:commands.Context, slope:int=3, yinter:int=3, min_:int=-20, max_:int=20):
        xaxis = numpy.arange(min_, max_, 0.1)
        yaxis = []
        for x in xaxis:
            yaxis += [slope*x+yinter]
        plt.plot(xaxis, yaxis)
        showy = f"{slope}x"
        if yinter != 0: showy += ["+",""][yinter<0] + str(yinter)
        plt.savefig("cache/plot.png")
        plt.grid()
        
        await ctx.send(file=nextcord.File("cache/plot.png", filename=f"{showy}.png"))
        plt.close()
    
    @CogCommand("prime")
    async def prime(self, ctx:commands.Context, n:int=12):
        if n <= 0: raise Exception('Cannot Factor Nonpositive Value')
        def handleexpo(expo) -> str:
            if expo==1:
                return ''
            return ''.join(list("⁰¹²³⁴⁵⁶⁷⁸⁹")[int(digit)] for digit in str(expo))
        await ctx.send(f"{n} = {' * '.join([f'{p}{handleexpo(e)}' for p, e in primefactor(n).items()])}")
        
    @CogCommand("factor")
    async def factor(self, ctx:commands.Context, n:int=12):
        if n <= 0: raise Exception('Cannot Factor Nonpositive Value')
        pfactors=primefactor(n)
        if math.prod([x+1 for x in pfactors.values()])>1_000_000:
            raise Exception('Too Many Factors')
        factors=[1]
        for p,e in pfactors.items():
            if p==1: # don't duplicate entries when 1 is present
                continue
            newfactors=[]
            for i in range(e+1): # inclusive
                factor=p**i
                newfactors+=[factor*f for f in factors]
            factors=newfactors
        factors.sort() # in place sort
        await ctx.send(f"{n} has {len(factors)} factors: \n{', '.join(map(str,factors))}")
        
def setup(bot):
	bot.add_cog(Math(bot))
