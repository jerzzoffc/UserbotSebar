from command import qrcode_cmd
from helpers import CMD

__MODULES__ = "Qrcode"
__HELP__ = """<blockquote>Command Help **Qr-Code** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **Generate image qrcode from text**
        `{0}qr gen` (code)
    **Get text code from qr image**
        `{0}qr read` (reply image)</blockquote>
<b>   {1}</b>
"""
IS_PRO = True


@CMD.UBOT("qr")
async def _(client, message):
    return await qrcode_cmd(client, message)
