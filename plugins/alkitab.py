__MODULES__ = "Alkitab"
__HELP__ = """<blockquote>Command Help **Alkitab**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search by word in the bible**
        `{0}alkitab` (query)</blockquote>
<b>   {1}</b>
"""


from command import alkitab_cmd
from helpers import CMD

IS_BASIC = True


@CMD.UBOT("alkitab")
async def _(client, message):
    return await alkitab_cmd(client, message)
