import glob
import nextcord
import datetime
import random
from pyfunc.lang import botinit, devs
from nextcord.ext import commands, tasks
from pyfunc.lang import cfg, evl, keywords, phraser, phrasermodule, getkws
from pyfunc.gettoken import gettoken
from pyfunc.commanddec import MainCommand
from pyfunc.block import get
import nextcord

botinit()
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
TimeOn = None
# initialize some things
keywords = getkws()

# reload the command locale
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

# get help for a command or display info about the bot
@MainCommand(bot,"help")
async def help(ctx, cmdname=None):
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
        sembed.description = evl("help.helplist.desc").format("\n".join(preparedlist))
        await interaction.send(ephemeral=True, embed=sembed)

    if not cmdname:
        # send an info embed about the bot if no command given
        embed = nextcord.Embed()
        if cfg('ShowHost'):
            showdisplay = evl("help.blankdisplay.server").format(cfg('HostDCID'))
        else:
            showdisplay = ""
        embed.description = evl("help.blankdisplay").format(datetime.datetime.now()-TimeOn, showdisplay)
        view = nextcord.ui.View()
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn) # with a button that prints a list of commands
        await ctx.send(embed=embed, view=view)
    else:
        # search through the commands and their aliases
        cmds={alias:cmd for cmd in bot.commands for alias in cmd.aliases+[cmd.name]}
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
    print(s)
    await ctx.send(s)

# represent sear's sanity
@MainCommand(bot,"scream")
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)

# send a link
@MainCommand(bot,"link")
async def link(ctx, typ="r2d"):
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

@tasks.loop(seconds=60)
async def changepresence():
    statuses = cfg("botInfo.Messages") # General whole Statuses
    categories = list(statuses.keys()) # Keys
    weights = [len(statuses[c]) for c in categories] # Weights of keys
    category = random.choices(categories,weights)[0] # Choosing a category
    status = random.choice(statuses[category]) # Status Message
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
    print(cog_name, "LOAD")
    bot.load_extension(cog_name[:-3])

# and run the bot
bot.run(token)
