from command import bingai_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Bingai"
__HELP__ = """<blockquote>Command Help **Bingai**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate image ai with Bingai from prompt command**
        `{0}bingai` (prompt)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("bingai")
async def _(client, message):
    return await bingai_cmd(client, message)
