from command import tg_cmd
from helpers import CMD

__MODULES__ = "Graph"
__HELP__ = """<blockquote>Command Help **Graph**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can upload text or media to telegraph then get url**
        `{0}tg` (reply text/reply media)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("tg")
async def _(client, message):
    return await tg_cmd(client, message)
