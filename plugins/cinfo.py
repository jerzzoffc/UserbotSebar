from command import cardinfo_cmd
from helpers import CMD

__MODULES__ = "Cardinfo"
__HELP__ = """<blockquote>Command Help **Cardinfo**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get information about user**
        `{0}cid` (username/reply user)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("cardinfo|cid")
async def _(client, message):
    return await cardinfo_cmd(client, message)
