from command import button_cmd, buttonch_cmd
from helpers import CMD

__MODULES__ = "Button"
__HELP__ = """<blockquote>Command Help **Button** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can create buttons from the text**
        `{0}button` (reply text)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("buttonch")
async def _(client, message):
    return await buttonch_cmd(client, message)


@CMD.UBOT("button")
async def _(client, message):
    return await button_cmd(client, message)
