__MODULES__ = "Anime"
__HELP__ = """<blockquote>Command Help **Anime**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get news update Anime**
        `{0}anime`</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

from command import infoanime_cmd
from helpers import CMD


@CMD.UBOT("anime")
async def _(_, message):
    return await infoanime_cmd(_, message)
