__MODULES__ = "Kbbi"
__HELP__ = """<blockquote>Command Help **Kbbi**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search words from KBBI**
        `{0}kbbi` (text/reply text)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


from command import kbbi_cmd
from helpers import CMD


@CMD.UBOT("kbbi")
async def _(client, message):
    return await kbbi_cmd(client, message)
