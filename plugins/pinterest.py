__MODULES__ = "Pinterest"
__HELP__ = """<blockquote>Command Help **Pinterest**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Download media from pinterest by title**
        `{0}pint` (title)</blockquote>
<b>   {1}</b>
"""


from command import pinterst_search
from helpers import CMD

IS_PRO = True


@CMD.UBOT("pint")
async def _(client, message):
    return await pinterst_search(client, message)
