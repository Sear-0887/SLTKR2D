import nextcord
from nextcord.ext import commands
from pyfunc.commanddec import CogCommand, InteractionCogCommand_Local
from pathlib import Path
import os
import time


class Misc(commands.Cog):
    def __init__(self, bot, branch):
        self.bot = bot
        self.branch = branch
        
    @CogCommand("branch")
    async def branch(self, ctx:commands.Context):
        await ctx.send(f"Current branch is {self.branch}")
        
    @InteractionCogCommand_Local("timestamp")
    async def timestamp(self, 
                     interaction: nextcord.Interaction, 
                     offsetsecond: int = 0,
                     formating: str|None=None):
        formatinfo = {
            "t": "Short Time",
            "T": "Long Time",
            "d": "Short Date",
            "D": "Long Date",
            "f": "Short Date/Time",
            "F": "Long Date/Time",
            "R": "Relative Time"
        }
        currenttime = int(time.time())-offsetsecond
        if formating is None:
            await interaction.response.send_message(f"Default | <t:{currenttime}> \n") 
        else:
            if formating in formatinfo.keys():
                await interaction.response.send_message(f"<t:{currenttime}:{formating}>") 
            elif formating.lower() in ["list", "listing", "l", "all"]:
                dump = f"Default | <t:{currenttime}> \n"
                for crfm in formatinfo.keys():
                    dump += f"{formatinfo[crfm]} | <t:{currenttime}:{crfm}> \n"
                await interaction.response.send_message(dump) 
            else:
                raise KeyError
    

def setup(bot):
    # https://stackoverflow.com/a/62724213
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r", encoding="utf-8") as f: content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            branch=line.partition("refs/heads/")[2]
            break

    # https://stackoverflow.com/a/77686288
    #process = subprocess.Popen(["git", "branch", "--show-current"], stdout=subprocess.PIPE)
    #branch_name, branch_error = process.communicate()

    bot.add_cog(Misc(bot,branch))