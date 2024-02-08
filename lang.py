keywords = {
    "Roody:2D Game Discord Server": {
        "link": "https://discord.gg/gbEkBNt",
        "kw": ["r2d", "roody2d", "roody:2d", "game", "gameser", "gamedc"]
    },
    "SLTK Wiki Server": {
        "link": "https://discord.gg/cDAUYrtjzV",
        "kw": ["sltk", "wikiser", "wikidc", "r2dwiki", "r2dwikiser"]
    },
    "SLTK Wiki Page": {
        "link": "https://roody2d.wiki.gg",
        "kw": ["wiki", "sltkwiki", "wikipage", "r2dwiki"]
    }
}

linksstr="".join([
    f"{name} ({data['link']})\nKeywords: {', '.join(data['kw'])}\n"
    for name,data in keywords.items()
])

class cmds:
    class help: 
        aliases = ["h"]
        syntax = "!help <cmd>"
        desc = """
            Displays what command <cmd> does.
            If left blank, shows info about the bot.
        """
        error = "Please provide a valid command name."
        blankdisplay = """
            # SLTK R2D
            A Roody:2D Utility Bot that displays useful information.
            PREFIX: !
            Please use the command !help <cmd> to view what !<cmd> does.
            SLTKR2D by <@697801071208300574>, All rights reserved.
            Time Since Last Restart: %s
            This bot is open-source on [Github](https://github.com/Sear-0887/SLTKR2D).
        """
    class ping:
        aliases      = []
        syntax     = "!ping"
        desc       = "Pong! + Display the latency of bot in ms."
        error      = "This is a error message"

    class scream:
        aliases      = ["AAAAA"]
        syntax     = "!scream"
        desc       = "*It symbolizes my sanity*"
        error      = "This is a error message"

    class block:
        aliases      = ["blk", "blkinfo", "binfo"]
        syntax     = "!block <blk>"
        desc       = "Allow you to view <blk>'s properties & icon. if left blank, it gives a random block.\nSupports using name or ID."
        error      = "Unable to find block %s."
    
    class link:
        aliases      = ["l", "lnk", "www"]
        syntax     = "!link <keyword>"
        desc       = f"""
            Allow you to mention various game-related links through <keyword>.
            Currently supports these links:
            {linksstr}
        """
        error      = "Unable to find link through %s"
    class image:
        aliases      = ["img", "i", "blockimg"]
        syntax     = "!image <string>"
        desc       = """
            Makes an image from <string> in the format of recipe.smp.
            Can use block name or ID.
            Note that this function is still unfinished.
            Examples: [[cast_iron][wire_spool]][[cast_iron][cast_iron]] - arc_furnace recipe
            Examples: [[16][20]] [[16][20]] - Same recipe
        """
        error      = "Unable to form image."    class viewcog:
        alias      = ["cg", "vcg", "cog"]
        syntax     = "!viewcog"
        desc       = """
            Read the current status of cogs detected.
            Admin-Only Command.
        """
        cmddisplay = "%s - %s (%s)"
        error      = "Unable to reach all cogs."
