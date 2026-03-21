from command import (gban_cmd, gbanlist_cmd, gmute_cmd, gmutelist_cmd,
                     ungban_cmd, ungmute_cmd)
from helpers import CMD

__MODULES__ = "Global"
__HELP__ = """<blockquote>Command Help **Global**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can global banned user from all chats youre admins**
        `{0}gban` (username)
    **Un-global ban user from all chats youre admins**
        `{0}ungban` (username)
    **View user you have gbanned**
        `{0}gbanlist`</blockquote>
        
<blockquote expandable>--**Gmute Commands**--

    **Mute the user from all chats youre admins**
        `{0}gmute` (username)
    **Un-global mute the user from all chats youre admins**
        `{0}ungmute` (username)
    **View user you have gmuted**
        `{0}gmutelist`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("gban")
@CMD.FAKEDEV("gban")
async def _(client, message):
    return await gban_cmd(client, message)


@CMD.UBOT("ungban")
@CMD.FAKEDEV("ungban")
async def _(client, message):
    return await ungban_cmd(client, message)


@CMD.UBOT("gbanlist")
@CMD.FAKEDEV("gbanlist")
async def _(client, message):
    return await gbanlist_cmd(client, message)


@CMD.UBOT("gmute")
@CMD.FAKEDEV("gmute")
async def _(client, message):
    return await gmute_cmd(client, message)


@CMD.UBOT("ungmute")
@CMD.FAKEDEV("ungmute")
async def _(client, message):
    return await ungmute_cmd(client, message)


@CMD.UBOT("gmutelist")
@CMD.FAKEDEV("gmutelist")
async def _(client, message):
    return await gmutelist_cmd(client, message)
