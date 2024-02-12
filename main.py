import glob
import nextcord
import datetime
from assetload import init
from nextcord.ext import commands
from lang import cmds, keywords
from gettoken import gettoken
from commanddec import command

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
print(cmds.ping.desc)

init()

@command(bot,"help")
async def help(ctx, cmdname=None,):
    if not cmdname:
        embed = nextcord.Embed()
        embed.description = cmds.help.blankdisplay.format(datetime.datetime.now()-TimeOn)
        view = nextcord.ui.View()
        async def gethelplist(interaction):
            sembed = nextcord.Embed()
            sembed.title = "Help List"
            sembed.description = "Here's a list of commands:\n" + ", ".join([cmd for cmd in dir(cmds) if not cmd.startswith("__")])
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
                cmd = getattr(cmds,cmdname)
                embed.title = cmdname
                embed.description = cmd.desc
                embed.add_field(name="Syntax", value=cmd.syntax)
                embed.add_field(name="Aliases", value=",\n".join(cmd.aliases))
                await ctx.send(embed=embed)
                return
        else:
            await ctx.send(cmds.help.error)

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

token = gettoken()
for cog_name in glob.glob("cog_*.py"):
    print(cog_name, "LOAD")
    bot.load_extension(cog_name[:-3])
bot.run(token)
