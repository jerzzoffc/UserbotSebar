from command import tiny_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Tiny"
__HELP__ = """<blockquote>Command Help **Tiny**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can resize the sticker to small**
        `{0}tiny` (reply image)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("tiny")
async def _(client, message):
    return await tiny_cmd(client, message)
