from command import qcolor_cmd, qoutly_cmd
from helpers import CMD

__MODULES__ = "Quote"
__HELP__ = """<blockquote>Command Help **Quote**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can make quote from text random color**
        `{0}q` (reply message)
    **You can make quote from text using costum color**
        `{0}q pink` (reply message)
    **You can make fake quote user the message with this message**
        `{0}q @navyfavbot` (reply message)
    **You can make fake quote user with replies and costum color**
        `{0}q @navyfavbot pink -r` (reply message)</blockquote>

<blockquote expandable>--**Extras Commands**--

    **You can make quote text with replies**
        `{0}q -r` (reply message)
    **You can make quote text with replies and costum color**
        `{0}q -r pink` (reply message)
    **You can make more quote text**
        `{0}q 5 ` (reply message)
    **You can make more quote text using costum color**
        `{0}q 5 pink` (reply message)
    **Get supported color for quote**
        `{0}qcolor`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("q|qcolor")
async def _(client, message):
    if message.command[0] == "qcolor":
        return await qcolor_cmd(client, message)
    elif message.command[0] == "q":
        return await qoutly_cmd(client, message)
