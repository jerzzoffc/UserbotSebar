from command import startnest_cmd
from helpers import CMD

__MODULES__ = "Starnest"
__HELP__ = """<blockquote>Command Help **Starnest**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate image using Starnest** 
        `{0}starnest` (prompt) </blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("starnest")
async def _(client, message):
    return await startnest_cmd(client, message)
