import os
import glob
import nextcord
from assetload import init, blockinfos, quickidtable
import keep_alive
import datetime
import random
import re
from dotenv import dotenv_values
from io import BytesIO
from PIL import Image
from nextcord.ext import commands
from lang import cmd, keywords
import block_extra as be

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmd.ping.desc)
init()

    
@bot.command(name="help", description=cmd.help.desc, aliases=cmd.help.alias)
async def help(ctx, tcmd=None,):
    if not tcmd:
        embed = nextcord.Embed()
        embed.description = cmd.help.blankdisplay % (datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        async def gethelplist(interaction):
            sembed = nextcord.Embed()
            sembed.title = "Help List"
            sembed.description = "Here's a list of commands:\n" + ", ".join([func for func in dir(cmd) if not func.startswith("__")])
            await interaction.send(ephemeral=True, embed=sembed)
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn)
        await ctx.send(embed=embed, view=view)
    else:
        for i in bot.all_commands:
            if tcmd in bot.all_commands[i].aliases:
                tcmd = i
            if tcmd == i:
                embed = nextcord.Embed()
                clas = eval(f"cmd.{tcmd}")
                desc = clas.desc
                if tcmd == "link":
                    container = ""
                    for cr in keywords:
                        container += "%s (%s)\nKeywords: %s\n" % (cr, keywords[cr]["link"], ", ".join(keywords[cr]["kw"]))
                    desc = desc % container
                embed.title = tcmd
                embed.description = desc
                embed.add_field(name="Syntax", value=clas.syntax)
                embed.add_field(name="Aliases", value=",\n".join(clas.alias))
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(cmd.help.error)

@bot.command(name="ping", description=cmd.ping.desc, aliases=cmd.ping.alias)
async def ping(ctx):
    print(cmd.ping.cmddisplay % (bot.latency*1000))
    await ctx.send(cmd.ping.cmddisplay % (bot.latency*1000))
    
@bot.command(name="scream", description=cmd.scream.desc, aliases=cmd.scream.alias)
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)
   
@bot.command(name="link", description=cmd.link.desc, aliases=cmd.link.alias)
async def link(ctx, typ="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(cmd.link.cmddisplay % (i, keywords[i]["link"]))
            return
    else:
        await ctx.send(cmd.link.error % typ)
        
@commands.has_permissions(administrator=True)
@bot.command(name="viewcog", description=cmd.viewcog.desc, aliases=cmd.viewcog.alias)
async def viewcog(ctx):
    embed = nextcord.Embed()
    embed.description = ""
    for cog_name in glob.glob("cog_*.py"):
        print([dir(o) for i, o in bot.cogs.items()])
        print([o.__cog_name__ for i, o in bot.cogs.items()])
        embed.description += "| %s \n" % cog_name[:-3]
    await ctx.send(embed=embed)
@commands.has_permissions(administrator=True)
@bot.command(name="cog_load", description=cmd.loadcog.desc, aliases=cmd.loadcog.alias)
async def loadcog(ctx, tar):
    try:
        bot.load_extension("cog_"+tar)
        await ctx.send("LOADED "+"cog_"+tar+".py")
    except commands.errors.ExtensionAlreadyLoaded:
        await ctx.send("cog_"+tar+".py is already loaded.")
    except commands.errors.ExtensionNotFound:
        await ctx.send("cog_"+tar+".py not found.")
        
@commands.has_permissions(administrator=True)
@bot.command(name="cog_unload", description=cmd.unloadcog.desc, aliases=cmd.unloadcog.alias)
async def unloadcog(ctx, tar):
    try:
        if tar == "cog_admin": raise commands.errors.ExtensionNotFound # prevent softlock
        bot.unload_extension("cog_"+tar)
        await ctx.send("UNLOADED "+"cog_"+tar+".py")
    except commands.errors.ExtensionAlreadyLoaded:
        await ctx.send("cog_"+tar+".py is already unloaded.")
    except commands.errors.ExtensionNotFound:
        await ctx.send("cog_"+tar+".py not found.")
        
@commands.has_permissions(administrator=True)
@bot.command(name="cog_reload", description=cmd.reloadcog.desc, aliases=cmd.reloadcog.alias)
async def unloadcog(ctx, tar):
    try:
        bot.unload_extension("cog_"+tar)
        await ctx.send("RELOADED "+"cog_"+tar+".py")
    except commands.errors.ExtensionNotFound:
        await ctx.send("cog_"+tar+".py not found.")        
        

@bot.event
async def on_ready():
    print("ONLINE as %s, id %s." % (bot.user, bot.user.id))
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now()
    
# def returniscog(cogname):
#     return bot.get_cog(cogname)

token = dotenv_values("cred/.env")['TOKEN']
for cog_name in glob.glob("cog_*.py"):
    print(cog_name, "LOAD")
    bot.load_extension(cog_name[:-3])
    print(bot.cogs)
keep_alive.keep_alive()
bot.run(token)