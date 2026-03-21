from command import remini_cmd
from helpers import CMD

__MODULES__ = "Remini"
__HELP__ = """<blockquote>Command Help **Remini HD**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Enchancer image to hd** 
        `{0}remini` (prompt) </blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("remini")
async def _(client, message):
    return await remini_cmd(client, message)
