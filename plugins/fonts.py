from command import font_cmd
from helpers import CMD

__MODULES__ = "Fonts"
__HELP__ = """<blockquote>Command Help **Fonts**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can make text to awesome from this command**
        `{0}font` (text/reply text)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("font")
async def _(client, message):
    return await font_cmd(client, message)
