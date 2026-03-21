from command import (bl_leave, cleardb_leave, getbl_leave, getmute_cmd,
                     join_cmd, kickme_cmd, leave_cmd, unbl_leave)
from helpers import CMD

__MODULES__ = "Extras"
__HELP__ = """<blockquote>Command Help **Extras**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can leave all channel from your account, except youre admin and blacklist leave**
        `{0}leave channel`
    **You can leave all channel and group, except youre admin and blacklist leave**
        `{0}leave global`
    **You can leave all chat group if you restricted**
        `{0}leave mute`
    **You can leave all chat group, except youre admin and blacklist leave**
        `{0}leave group`

    **You can leave this chat now**
        `{0}kickme`
    **This command for check, where you has been restricted from chat**
        `{0}getmute`
    **You can join to chat use id, url, or username**
        `{0}join` (chatid)</blockquote>

<blockquote expandable>--**BL-Leave Commands**--

    **Add chat to blacklist leave if you want**
        `{0}bl-leave` (chatid)
    **Delete chat from blacklist leave from  your account**
        `{0}unbl-leave` (chatid)
    **You can view all chats on blacklist leave**
        `{0}getbl-leave`
    **Or you can clear or delete all chats on blacklist leave**
    `{0}cleardb-leave`

**Note**: For the blacklist leave, when you use the leave command then you will not leave from db leave blacklist. </blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("getmute")
@CMD.FAKEDEV("getmute")
async def _(client, message):
    return await getmute_cmd(client, message)


@CMD.UBOT("join")
@CMD.FAKEDEV("join")
async def _(client, message):
    return await join_cmd(client, message)


@CMD.UBOT("kickme")
async def _(client, message):
    return await kickme_cmd(client, message)


@CMD.UBOT("leave")
@CMD.FAKEDEV("leave")
async def _(client, message):
    return await leave_cmd(client, message)


@CMD.UBOT("bl-leave")
async def _(client, message):
    return await bl_leave(client, message)


@CMD.UBOT("unbl-leave")
async def _(client, message):
    return await unbl_leave(client, message)


@CMD.UBOT("getbl-leave")
async def _(client, message):
    return await getbl_leave(client, message)


@CMD.UBOT("cleardb-leave")
async def _(client, message):
    return await cleardb_leave(client, message)
