from command import pastebin_cmd
from helpers import CMD

"""
__MODULES__ = "Pastebin"
__HELP__ = <blockquote>Command Help **Pastebin** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can post text to pastebin**
        `{0}paste` (reply text/document)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("bin|paste")
async def _(client, message):
    return await pastebin_cmd(client, message)
