from command import khodam_cmd
from helpers import CMD

__MODULES__ = "Wapak"
__HELP__ = """<blockquote>Command Help **Wapak**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can check wapak of person**
        `{0}wapak` (reply user/username)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("khodam|kodam|wapak")
async def _(client, message):
    return await khodam_cmd(client, message)
