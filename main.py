import glob
import nextcord
import datetime
from assetload import init
from nextcord.ext import commands
from lang import keywords, phraser, cmdi, evl
from gettoken import gettoken
from commanddec import command
import os

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

phraser()
init()


@command(bot,"help")
async def help(ctx, cmdname=None,):
    if not cmdname:
        embed = nextcord.Embed()
        embed.description = evl("help.blankdisplay").format(datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        async def gethelplist(interaction):
            sembed = nextcord.Embed()
            sembed.title = "Help List"
            sembed.description = "Here's a list of commands:\n" + ", ".join(cmdi.keys())
            await interaction.send(ephemeral=True, embed=sembed)
        getlistbtn = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label="Help List")
        getlistbtn.callback = gethelplist
        view.add_item(getlistbtn)
        await ctx.send(embed=embed, view=view)
    else:
        for i in bot.all_commands:
            if cmdname in bot.all_commands[i].aliases:
                cmdname = i
            if cmdname == i:
                embed = nextcord.Embed()
                embed.title = cmdname
                embed.description = evl(f"{cmdname}.desc")
                embed.add_field(name="Syntax", value=evl(f"{cmdname}.syntax"))
                embed.add_field(name="Aliases", value=",\n".join(evl(f"{cmdname}.aliases")))
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(evl(f"{cmdname}.error"))

@command(bot,"ping")
async def ping(ctx):
    s=f"Pong! ({bot.latency*1000} ms)"
    print(s)
    await ctx.send(s)
    
@command(bot,"scream")
async def scream(ctx, n:int=32):
    await ctx.send("A"*n)

@command(bot,"link")
async def link(ctx, typ="r2d"):
    for i in keywords:
        if typ in keywords[i]["kw"]:
            await ctx.send(f"`{i}` - {keywords[i]['link']}")
            return
    else:
        raise Exception('')
        #await ctx.send(cmds.link.error % typ)

@commands.has_permissions(administrator=True)
@command(bot,'test')
async def test(ctx):
    await ctx.send('!help')

@bot.event
async def on_ready():
    print(f"ONLINE as {bot.user}, id {bot.user.id}.")
    print("Done.")
    global TimeOn
    TimeOn = datetime.datetime.now()
    
# def returniscog(cogname):
#     return bot.get_cog(cogname)

os.makedirs('cache',exist_ok=True)

token = gettoken()
for cog_name in glob.glob("cog_*.py"):
    print(cog_name, "LOAD")
    bot.load_extension(cog_name[:-3])
bot.run(token)
