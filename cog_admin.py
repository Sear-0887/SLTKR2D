import glob
from assetload import blockinfos, quickidtable, frs
import nextcord
import datetime
import random
import re
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import block_extra as be

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
            
def setup(bot):
	bot.add_cog(Admin(bot))