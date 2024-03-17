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
from pathlib import Path


class Branch(commands.Cog):
    def __init__(self, bot, branch):
        self.bot = bot
        self.branch = branch
        
    @CogCommand("branch")
    async def branch(self, ctx:commands.Context):
        await ctx.send(f"Current branch is {self.branch}")
        
def setup(bot):
    # https://stackoverflow.com/a/62724213
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f: content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            branch=line.partition("refs/heads/")[2]
            break

    # https://stackoverflow.com/a/77686288
    #process = subprocess.Popen(["git", "branch", "--show-current"], stdout=subprocess.PIPE)
    #branch_name, branch_error = process.communicate()

    bot.add_cog(Branch(bot,branch))