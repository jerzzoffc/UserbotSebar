from command import spam_cmd, spamg_cmd
from helpers import CMD

__MODULES__ = "Spam"
__HELP__ = """<blockquote>Command Help **Spam**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Send spam with delay**
        `{0}dspam` (reply message) (amount) (delay)
    **Send spam without delay**
        `{0}spam` (reply message) (amount)
    **Send spam broadcast with count**
        `{0}spamg` (count) (text/reply message)
    **Cancel task spam**
        `{0}cancel` (taskid)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("spam|dspam")
async def _(client, message):
    return await spam_cmd(client, message)


@CMD.UBOT("spamg")
async def _(client, message):
    return await spamg_cmd(client, message)
