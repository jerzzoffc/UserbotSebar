__MODULES__ = "Cat"
__HELP__ = """<blockquote>Command Help **Cat**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get random image cute cats**
        `{0}cats`</blockquote>
<b>   {1}</b>
"""


from command import cat_cmd
from helpers import CMD


@CMD.UBOT("cats")
async def _(_, message):
    return await cat_cmd(_, message)
