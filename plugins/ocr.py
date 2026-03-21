from command import ocr_cmd
from helpers import CMD

__MODULES__ = "Ocr"
__HELP__ = """<blockquote>Command Help **Ocr**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **This command can get text from the image**
        `{0}ocr` (reply image)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("ocr|read")
async def _(client, message):
    return await ocr_cmd(client, message)
