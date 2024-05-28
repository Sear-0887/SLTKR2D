import nextcord
from nextcord.ext import commands
from pyfunc.commanddec import CogCommand, InteractionCogCommand_Local
from pathlib import Path
import os
import time
from datetime import datetime, timezone


class Misc(commands.Cog):
    def __init__(self, bot:commands.Bot, gitbranch:str) -> None:
        self.bot = bot
        self.gitbranch = gitbranch
        
    @CogCommand("branch")
    async def branch(self, ctx:commands.Context) -> None:
        await ctx.send(f"Current branch is {self.gitbranch}")
        
    @InteractionCogCommand_Local("timestamp")
    async def timestamp(self, 
                     interaction: nextcord.Interaction, 
                     year   : int = nextcord.SlashOption(required=False, default=None),
                     month  : int = nextcord.SlashOption(required=False, default=None),
                     day    : int = nextcord.SlashOption(required=False, default=None),
                     hour   : int = nextcord.SlashOption(required=False, default=None),
                     minute : int = nextcord.SlashOption(required=False, default=None),
                     second : int = nextcord.SlashOption(required=False, default=None),
                     formating:str = nextcord.SlashOption(name="formating", required=False, choices=[
                        "Default",
                        "List All",
                        "Short Time",
                        "Long Time",
                        "Short Date",
                        "Long Date",
                        "Short Date/Time",
                        "Long Date/Time",
                        "Relative Time"
                    ], default="Default")) -> None:
        formatings = {
                        "Default": "",
                        "Short Time": ":t",
                        "Long Time": ":T",
                        "Short Date": ":d",
                        "Long Date": ":D",
                        "Short Date/Time": ":f",
                        "Long Date/Time": ":F",
                        "Relative Time": ":R"
                    }
        currenttime = int(
        datetime(
        year   = year   or datetime.now().year,
        month  = month  or datetime.now().month,
        day    = day    or datetime.now().day,
        hour   = hour   or datetime.now().hour,
        minute = minute or datetime.now().minute,
        second = second or datetime.now().second
        ).timestamp())
        if formating == "List All":
            await interaction.response.send_message(
                "\n".join([
                    f"{key} | <t:{currenttime}{item}>" for key, item in formatings.items()
                ])) 
        else:
            await interaction.response.send_message(f"{formating} | <t:{currenttime}{formatings[formating]}>") 
                
    

def setup(bot:commands.Bot) -> None:
    # https://stackoverflow.com/a/62724213
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r", encoding="utf-8") as f: content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            branch=line.partition("refs/heads/")[2]
            break


    bot.add_cog(Misc(bot,branch))