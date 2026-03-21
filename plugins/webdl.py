from command import webdl_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Webdl"
__HELP__ = """<blockquote>Command Help **Webdl**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get html code from url**
        `{0}webdl` (url)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("webdl")
async def _(client, message):
    return await webdl_cmd(client, message)
