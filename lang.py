class cmd:
    class help: 
        alias = ["h"]
        syntax = "!help <cmd>"
        desc = """
            Displays what command <cmd> does.
            if left blank, it will show bot's info.
        """
        cmddisplay = "/"
        error = "Please Provide a valid command name."
        blankdisplay = """
            # SLTK R2D
            A Roody:2D Utility Bot that displays useful informations.
            PREFIX: !
            Please use the command !help <cmd> to view what the <cmd> does.
            SLTKR2D by <@697801071208300574>, All right's reserved.
            Bot Since Last restart: %s
            This bot is open-sourced on Github in [Here](https://github.com/Sear-0887/SLTKR2D).
        """
    class ping:
        alias      = []
        syntax     = "!ping"
        desc       = "Pong! + Display the latency of bot in ms."
        cmddisplay = "Pong! (%s ms)"
        error      = "This is a error message"

    class scream:
        alias      = ["AAAAA"]
        syntax     = "!scream"
        desc       = "*It symboilizes my sanity*"
        cmddisplay = "/"
        error      = "This is a error message"

    class block:
        alias      = ["blk", "blkinfo", "binfo"]
        syntax     = "!block <blk>"
        desc       = "Allow you to view block <blk>'s properties & icon. if left blank, it gives a random block.\nSupport finding by name or ID."
        cmddisplay = "/"
        error      = "Unable to find block %s."
    
    class link:
        alias      = ["l", "lnk", "www"]
        syntax     = "!link <keyword>"
        desc       = """
            Allow you to mention various game-related links through <keyword>.
            Currently Support these links:
            %s
        """
        cmddisplay = "`%s` - %s"
        error      = "Unable to find link through %s"
    class image:
        alias      = ["img", "i", "blockimg"]
        syntax     = "!image <string>"
        desc       = """
            Allow you to build in-game recipe through <string> in the format of recipe.smps.
            Note that this function is still unfinished.
            Examples: [[cast_iron][wire_spool]][[cast_iron][cast_iron]] - arc_furnace recipe
            Examples: [[16][20]] [[16][20]] - Same recipe
        """
        cmddisplay = "/"
        error      = "Unable to form image."

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