from command import spam_bot
from helpers import CMD

__MODULES__ = "Spambot"
__HELP__ = """<blockquote>Command Help **Spambot**</blockquote> 
<blockquote expandable>--**Basic Commands**--

    **Check your status account from limit @spambot**
        `{0}limit`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("limit")
@CMD.FAKEDEV("limit")
async def _(client, message):
    return await spam_bot(client, message)
