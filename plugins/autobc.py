from command import autobc_cmd
from helpers import CMD

__MODULES__ = "Autobc"
__HELP__ = """<blockquote>Command Help **Autobc**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Add text for autobc**
        `{0}autobc add` (reply text)
    **Set auto gcast on or off, before you set this please add text first**
        `{0}autobc` (on/off)
    **Delete text from list auto gcast**
        `{0}autobc del` (number)
    **You can set on for notification check limit from @spambot**
        `{0}autobc limit` (on/off)
    **You can set delay for auto gcast**
        `{0}autobc delay` (number)
    **You can check all message text auto gcast**
        `{0}autobc get`
    **You can set where to send on topic mode**
        `{0}autobc topic`
 
**Note**: please add the text first, before enable autobc.</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("autobc")
async def _(client, message):
    return await autobc_cmd(client, message)
