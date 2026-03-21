from command import webss_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Webshot"
__HELP__ = """<blockquote>Command Help **Webshot** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get screenshot web from url**
        `{0}webss` (url)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("webss")
async def _(client, message):
    return await webss_cmd(client, message)
