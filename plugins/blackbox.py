__MODULES__ = "Blackbox"
__HELP__ = """<blockquote>Command Help **Blackbox**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer question to blackbox ai** 
        `{0}blackbox` (question) 
    **You can answer about image to blackbox ai** 
        `{0}blackbox` (reply photo) (question) 
    **You can generate image to blackbox ai** 
        `{0}blackbox generate` (prompt)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

from command import blackbox_cmd
from helpers import CMD


@CMD.UBOT("blackbox")
async def _(client, message):
    return await blackbox_cmd(client, message)
