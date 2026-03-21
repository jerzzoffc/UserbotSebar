__MODULES__ = "Bola"
__HELP__ = """<blockquote>Command Help **Bola**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get news schedule football today's**
        `{0}bola`</blockquote>
<b>   {1}</b>
"""
IS_BASIC = True


from command import bola_cmd
from helpers import CMD


@CMD.UBOT("bola")
async def _(_, message):
    return await bola_cmd(_, message)
