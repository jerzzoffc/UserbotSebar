__MODULES__ = "Tiktok"
__HELP__ = """<blockquote>Command Help **Tiktok**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search video from tiktok by title**
        `{0}tiktok` (title)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


from command import tiktok_search
from helpers import CMD


@CMD.UBOT("tiktok")
async def _(client, message):
    return await tiktok_search(client, message)
