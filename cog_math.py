from pyfunc.assetload import blockinfos, idtoblock as quickidtable,locale
import matplotlib.pyplot as plt
import numpy
import nextcord
import random
import math
import re
import time
from PIL import Image
from collections import defaultdict
from nextcord.ext import commands
from pyfunc.lang import lprint
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
    
    # Copied from my old code, should run N (2≤N≤10^9) within 1 sec
    @CogCommand("prime")
    async def prime(self, ctx, n:int=12):
        def handleexpo(expo) -> str:
            if expo == 1: return ""
            cvexp = ''.join(['⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹'][int(digit)] for digit in str(expo))
            return cvexp
        start = time.perf_counter()
        r = n
        c = defaultdict(int)
        if n <= 1:
            c[n] = 1
        else:
            while n % 2 == 0:
                n //= 2
                c[2] += 1
            i = 1
            while n > 1:
                i += 2
                if i * i > n:
                    c[n] += 1
                    break
                while n % i == 0:
                    n //= i
                    c[i] += 1
        end = time.perf_counter()
        print("DONE CALCULATING, HANDLING")
        await ctx.send(f"{r} = {' * '.join([f'{base}{handleexpo(expo)}' for base, expo in c.items()])}")
        print(f"{1000*(end - start):.3f} ms") 
    # Near Same tested as !prime 
    @CogCommand("factor")
    async def factor(self, ctx:commands.Context, n:int=12):
        r = n
        m = int(math.sqrt(n))
        factor = []
        for i in range(1, m + 1):
            if n % i == 0:
                factor.append(str(i))
        if m * m == n:
            m -= 1
        for i in range(m, 0, -1):
            if n % i == 0:
                factor.append(str(n // i))
        await ctx.send(f"{r} has {len(factor)} factors: \n{', '.join(factor)}")
        
def setup(bot):
	bot.add_cog(Math(bot))