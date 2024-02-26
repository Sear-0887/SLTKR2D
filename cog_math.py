from assetload import blockinfos, idtoblock as quickidtable,locale
import nextcord
import random
import re
from PIL import Image
from nextcord.ext import commands

from commanddec import CogCommand


class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @CogCommand("eval")
    async def evalu(self, ctx:commands.Context, *, formulae="3 * ( 1 + 2 )"):
        global formu
        formu = formulae.replace(" ", "")
        def dif(x): return int(x) if int(float(x)) == float(x) else float(x)
        def removexcessbracket(formu):
            while True:
                elimb = re.findall(rf"\((\-?[\d\.]+)\)", formu)
                if elimb: 
                    elimb = elimb[0]
                    print(f"{(formu, elimb)=}")
                    formu = formu.replace(f"({elimb})", elimb)
                else:
                    break
            return formu
        while True:
            print(f">>> {formu=}")
            result = None
            for operator in "^*/+-":
                formu = removexcessbracket(formu)
                result = re.findall(rf"(\-?[\d\.]+)([\+\-\*\/\^])(\-?[\d\.]+)", formu)
                if result == []: continue
                f, operator, s = result[0]
                print(f, operator, s)
                if   operator == "^": operated = dif(f) ** dif(s)
                if   operator == "*": operated = dif(f) *  dif(s)
                elif operator == "/": operated = dif(f) /  dif(s)
                elif operator == "+": operated = dif(f) +  dif(s)
                elif operator == "-": operated = dif(f) -  dif(s)
                formu = formu.replace(f"{f}{operator}{s}", str(operated))
                formu = removexcessbracket(formu)
            if not result:
                print("PROPERE")
                break
            formu = dif(formu)
            
        await ctx.send(f"{formulae} = {formu}")   
            
        # global formu
        # formu = formulae
        # def dec(inp, formu):
        #     print(inp)
        #     if inp == []: return formu
        #     f, o, s = inp[0]
        #     f, s = int(f), int(s)
        #     result = None
        #     if o == "*": result = f * s
        #     if o == "/": result = f / s
        #     if o == "+": result = f + s
        #     if o == "-": result = f - s
        #     if result != None:
        #         replaced = formu.replace(str(f)+o+str(s), str(result))
        #         dec(re.findall(rf"(\d+)(\{o})(\d+)", replaced), replaced)
        #         return 
        #     return formu
        # formu = formu.replace(" ", "")
        # formu = dec(re.findall(r"(\d+)(\*)(\d+)", formu), formu)
        # formu = dec(re.findall(r"(\d+)(\/)(\d+)", formu), formu)
        # formu = dec(re.findall(r"(\d+)(\+)(\d+)", formu), formu)
        # formu = dec(re.findall(r"(\d+)(\-)(\d+)", formu), formu)
        
        
def setup(bot):
	bot.add_cog(Math(bot))