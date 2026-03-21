from command import carbon_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Carbon"
__HELP__ = """<blockquote>Command Help **Carbon**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate carbonara from text**
        `{0}carbon` (reply text)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("carbon|carbonara")
async def _(client, message):
    return await carbon_cmd(client, message)
