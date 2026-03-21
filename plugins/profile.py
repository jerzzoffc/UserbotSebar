from command import (adminlist_cmd, block_cmd, remuname_cmd, setbio_cmd,
                     setname_cmd, setonline_cmd, setpp_cmd, setuname_cmd,
                     unblock_cmd)
from helpers import CMD

__MODULES__ = "Profile"
__HELP__ = """<blockquote>Command Help **Profile** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **This command for check list your admins group**
        `{0}adminlist`
    **Get stats your account, like group counts, channel, bot, private messages**
        `{0}mestats`
    **You can block the user if you want**
        `{0}block` (username/reply user)
    **Unblock the user**
        `{0}unblock` (username/reply user)</blockquote>

<blockquote expandable>--**Profile Commands**--

    **You can set new username to your account**
        `{0}setuname` (text/reply text)
    **You delete the username from your account**
        `{0}remuname`
    **You can change bio from your account**
        `{0}setbio` (text/reply text)
    **You can set new name to your account**
        `{0}setname` (text/reply text)
    **You can set new profile photo to your account**
        `{0}setpp` (reply media)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("setonline")
async def _(client, message):
    return await setonline_cmd(client, message)


@CMD.UBOT("unblock")
async def _(client, message):
    return await unblock_cmd(client, message)


@CMD.UBOT("block")
async def _(client, message):
    return await block_cmd(client, message)


@CMD.UBOT("setname")
@CMD.FAKEDEV("setname")
async def _(client, message):
    return await setname_cmd(client, message)


@CMD.UBOT("setuname")
@CMD.FAKEDEV("setuname")
async def _(client, message):
    return await setuname_cmd(client, message)


@CMD.UBOT("remuname")
@CMD.FAKEDEV("remuname")
async def _(client, message):
    return await remuname_cmd(client, message)


@CMD.UBOT("setbio")
@CMD.FAKEDEV("setbio")
async def _(client, message):
    return await setbio_cmd(client, message)


@CMD.UBOT("adminlist")
async def _(client, message):
    return await adminlist_cmd(client, message)


@CMD.UBOT("setpp")
@CMD.FAKEDEV("setpp")
async def _(client, message):
    return await setpp_cmd(client, message)
