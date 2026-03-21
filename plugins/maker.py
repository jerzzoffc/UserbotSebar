from command import maker_img_cmd
from helpers import CMD

__MODULES__ = "Maker"
__HELP__ = """<blockquote>Command Help **Maker**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can make effect for photo**
        `{0}maker` (command) (reply photo)
    **Available command:**
    - `xnxx`
    - `sertifikat`</blockquote>
<b>   {1}</b>
"""
IS_PRO = True


@CMD.UBOT("maker")
async def _(client, message):
    return await maker_img_cmd(client, message)
