from command import chord_cmd
from helpers import CMD

__MODULES__ = "Chord"
__HELP__ = """<blockquote>Command Help **Chord**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get chord from the songs**
        `{0}chord` (title)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("chord")
async def _(client, message):
    return await chord_cmd(client, message)
