__MODULES__ = "Comic"
__HELP__ = """<blockquote>Command Help **Comic**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get news update Comic**
        `{0}comic`</blockquote>
<b>   {1}</b>
"""


from command import comic_cmd
from helpers import CMD

IS_PRO = True


@CMD.UBOT("comic")
async def _(_, message):
    return await comic_cmd(_, message)
