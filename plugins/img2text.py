__MODULES__ = "Img2text"
__HELP__ = """<blockquote>Command Help **Img2 Text**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get prompt command for generate image from reply image**
        `{0}img2text` (reply to image)</blockquote>
<b>   {1}</b>
"""

from command import img2text_cmd
from helpers import CMD

IS_BASIC = True


@CMD.UBOT("img2text")
async def _(client, message):
    return await img2text_cmd(client, message)
