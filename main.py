import glob
import nextcord
import logging
import os
from pyfunc.log import LoggerInit
import yaml
import datetime
import random
from pyfunc.lang import botinit, devs
from nextcord.ext import commands, tasks
from pyfunc.lang import cfg, evl, keywords, phraser, phrasermodule, getkws, getpresense
from pyfunc.gettoken import gettoken
from pyfunc.commanddec import MainCommand
from pyfunc.block import get
LoggerInit()
l = logging.getLogger()
l.info("Logging System Loaded!")
botinit()
# Intents
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
# Bot Instance
bot = commands.Bot(command_prefix=cfg("PREFIX"), intents=intents, help_command=None)
# TimeOn must be a datetime, or else error will be raised when !help
TimeOn: datetime.datetime = datetime.datetime.now() 
# initialize some things
keywords = getkws()
presencemsg = getpresense()


# Reloads the command locale
@MainCommand(bot, "reloadlocale")
async def reloadlocal(ctx,module=None):
    if module is None:
        phraser()
        #for i in bot.commands:
        #    i.update()
        await ctx.send("Done.")
    else:
        found=phrasermodule(module)
        if found:
            await ctx.send("Done.")
        else:
            await ctx.send(f"Did not find any locale files for {module}")

# Get help texts for a command or display info about the bot
@MainCommand(bot,"help")
async def help(ctx, cmdname:str | None=None):
    async def gethelplist(interaction:nextcord.Interaction):
        preparedlist = []
        for cmd in bot.commands:
            s=f"### !{cmd.name}"
            if len(cmd.aliases)>0: # don't have empty parens
                s+=f" ({'/'.join(cmd.aliases)})"
            s+=f"\n"
            s+=f"{cmd.description}"
            preparedlist.append(s)
        sembed = nextcord.Embed()
        sembed.title = evl("help.helplist.title")
        desc = evl("help.helplist.desc")
        assert isinstance(desc,str)
        sembed.description = desc.format("\n".join(preparedlist))
        await interaction.send(ephemeral=True, embed=sembed)

    if not cmdname:
        # send an info embed about the bot if no command given
        embed = nextcord.Embed()
        if cfg('ShowHost'):
            showdisplay = evl("help.blankdisplay.server")
            assert isinstance(showdisplay,str)
            showdisplay = showdisplay.format(cfg('HostDCID'))
        else:
            showdisplay = ""
        desc = evl("help.blankdisplay")
        assert isinstance(desc,str)
        embed.description = desc.format(datetime.datetime.now()-TimeOn, showdisplay)
        view = nextcord.ui.View()
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn) # Adding a button that prints a list of commands in an ephemeral embed
        await ctx.send(embed=embed, view=view)
    else:
        # search through the commands and their aliases
        cmds={alias:cmd for cmd in bot.commands for alias in [*cmd.aliases,cmd.name]}
        if cmdname in cmds:
            cmd=cmds[cmdname]
            embed = nextcord.Embed()
            embed.title = cmd.name
            embed.description = evl(f"{cmd.name}.desc")
            embed.add_field(name="Syntax", value=evl(f"{cmd.name}.syntax"))
            embed.add_field(name="Aliases", value=",\n".join(cmd.aliases))
            embed.add_field(name="Cog", value='Main' if cmd.cog_name == None else cmd.cog_name)
            await ctx.send(embed=embed)
        else:
            raise KeyError("Couldn't find the command") # the decorator will handle it

# check if the bot is up
@MainCommand(bot,"ping")
async def ping(ctx):
    s=f"Pong! ({bot.latency*1000} ms)"
    l.info(s)
    await ctx.send(s)

# represent sear's sanity
@MainCommand(bot,"scream")
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)
    
# represent sear's sanity... again?
@MainCommand(bot,"wee")
async def scream(ctx, e:int=32):
    await ctx.send("W"+"e"*e)

# send a link
@MainCommand(bot,"link")
async def link(ctx, typ:str="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(f"`{i}` - {keywords[i]['link']}")
            return
    else:
        raise KeyError('')

# credits to the developers
@MainCommand(bot,'credit')
async def credit(ctx):
    devstr = '\n'.join([f'### [{dev["name"]}]({dev["github_link"]}){dev["desc"]}' for dev in devs])
    await ctx.send(evl("credit.display").format(devstr))

# Presence Message Loop
@tasks.loop(seconds=60)
async def changepresence() -> None:
    statuses: dict[str, list] = presencemsg # General whole Statuses
    categories: list[str] = list(statuses.keys()) # Keys
    weights: list[int] = [len(statuses[c]) for c in categories] # Weights of keys
    category: str = random.choices(categories,weights)[0] # Choosing a category
    status: str = random.choice(statuses[category]) # Status Message
    types={
        'play':nextcord.ActivityType.playing,
        'listen':nextcord.ActivityType.listening,
        'watch':nextcord.ActivityType.watching,
    }
    presence=nextcord.Activity(type=types[category], name=status)
    print(f"Changed Presence to {category}: {status}")
    await bot.change_presence(status=nextcord.Status.online, activity=presence)

# the bot is ready now
@bot.event
async def on_ready():
    print(f"ONLINE as {bot.user} appearing {bot.user.display_name}, id {bot.user.id}.")
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now() # updating the real TimeOnline
    changepresence.start()


# get the bot token
token = gettoken()

# load all cogs
for cog_name in glob.glob("cog_*.py"):
    l.info(f"{cog_name} LOADED")
    bot.load_extension(cog_name[:-3])



# and run the bot
bot.run(token)
