from command import catur_cmd, game_cmd
from helpers import CMD

__MODULES__ = "Games"
__HELP__ = """<blockquote>Command Help **Games**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can send inline catur game to chat**
        `{0}catur`
    **For this command, you can send inline random games to this chat**
        `{0}game`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("catur")
async def _(client, message):
    return await catur_cmd(client, message)


@CMD.UBOT("game")
async def _(client, message):
    return await game_cmd(client, message)
