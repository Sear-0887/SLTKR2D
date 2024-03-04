import glob
import os
import nextcord
import datetime
from assetload import init
from nextcord.ext import commands
from lang import cfg, cmdi, config, evl, keywords, loadconfig, phraser
from gettoken import gettoken
from commanddec import MainCommand

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
TimeOn = datetime.datetime.now()
def botinit():
    os.makedirs(cfg('cache_folder'), exist_ok=True)
    os.makedirs(cfg('log_folder'), exist_ok=True)
    phraser()
    init() #assetload

botinit()
    
@MainCommand(bot, "reloadlocal")
async def reloadlocal(ctx):
    phraser()
    for i in bot.commands:
        i.update()
    await ctx.send("Done.")

@MainCommand(bot,"help")
async def help(ctx, cmdname=None,):
    async def gethelplist(interaction:nextcord.Interaction, helplist:list|str=[]):
        author = interaction.user
        preparedlist = []
        for key in bot.commands:
            if key.name in helplist or helplist == []:
                preparedlist.append(f"### {key.name} ({'/'.join(key.aliases)})")
                preparedlist.append(f"{key.description}")
        sembed = nextcord.Embed()
        sembed.title = evl("help.helplist.title")
        sembed.description = evl("help.helplist.desc").format("\n".join(preparedlist))
        
        await interaction.send(ephemeral=True, embed=sembed)
    if not cmdname:
        embed = nextcord.Embed()
        embed.description = evl("help.blankdisplay").format(datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn)
        await ctx.send(embed=embed, view=view)
    else:
        for cmd in bot.commands:
            if cmdname in cmd.aliases or cmdname == cmd.name:
                embed = nextcord.Embed()
                embed.title = cmd.name
                embed.description = evl(f"{cmdname}.desc")
                embed.add_field(name="Syntax", value=evl(f"{cmd.name}.syntax"))
                embed.add_field(name="Aliases", value=",\n".join(cmd.aliases))
                embed.add_field(name="Cog", value='Main' if cmd.cog_name == None else cmd.cog_name)
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(evl(f"{cmdname}.error"))

@MainCommand(bot,"ping")
async def ping(ctx):
    s=f"Pong! ({bot.latency*1000} ms)"
    print(s)
    await ctx.send(s)
    
@MainCommand(bot,"scream")
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)

@MainCommand(bot,"link")
async def link(ctx, typ="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(f"`{i}` - {keywords[i]['link']}")
            return
    else:
        raise Exception('')

@MainCommand(bot,'credit')
async def credit(ctx):
    dev = config['bot_info']['Developer']
    await ctx.send(evl("credit.display").format(dev[0]['github_link'], dev[1]['github_link']))

@bot.event
async def on_ready():
    print(f"ONLINE as {bot.user}, id {bot.user.id}.")
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now()


token = gettoken()
for cog_name in glob.glob("cog_*.py"):
    print(cog_name, "LOAD")
    bot.load_extension(cog_name[:-3])
bot.run(token)
