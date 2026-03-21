from command import brat_cmd
from helpers import CMD

__MODULES__ = "Brat"
__HELP__ = """<blockquote>Command Help **Brat**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can make brat video using costum text**
        `{0}vbrat` (text)
    **You can make brat image using costum text**
        `{0}brat` (text)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("brat|vbrat")
async def _(client, message):
    return await brat_cmd(client, message)
