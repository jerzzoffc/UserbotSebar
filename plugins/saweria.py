__MODULES__ = "Saweria"
__HELP__ = """<blockquote>Command Help **Saweria** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can login to saweria with this command**
        `{0}saweria login` (reply message with format email and username)
    **You can create a new payment with amount**
        `{0}saweria qris` (5000 beli kopi)
 **Note**: if you want use this feature, please login first.</blockquote>
<b>   {1}</b>
"""

from command import saweria_cmd
from helpers import CMD

IS_PRO = True


@CMD.UBOT("saweria")
async def _(client, message):
    return await saweria_cmd(client, message)
