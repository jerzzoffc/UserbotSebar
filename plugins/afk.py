from clients import navy
from command import REP_BLOCK
from helpers import AFK_, CMD

__MODULES__ = "AFK"
__HELP__ = """<blockquote>Command Help **AFK**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can set status to AFK mode**
        `{0}afk` (reason)
    **After AFK mode on, you can set to UNAFK mode**
        `{0}unafk`
    **You can set mode private/all, if mode set to private afk message only working on private**
        `{0}afk mode` (private/all)</blockquote>

<b>   {1}</b>
"""

IS_BASIC = True


@CMD.NO_CMD("REP_BLOCK", navy)
async def _(client, message):
    return await REP_BLOCK(client, message)


@CMD.UBOT("afk")
async def _(client, message):
    return await AFK_.set_afk(client, message)


@CMD.NO_CMD("AFK", navy)
async def _(client, message):
    return await AFK_.get_afk(client, message)


@CMD.UBOT("unafk")
async def _(client, message):
    return await AFK_.unset_afk(client, message)
