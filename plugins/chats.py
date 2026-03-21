from command import (cc_cmd, cekmember_cmd, cekmsg_cmd, cekonline_cmd,
                     create_cmd, endchat_cmd, getlink_cmd)
from helpers import CMD

__MODULES__ = "Chats"
__HELP__ = """<blockquote>Command Help **Chats**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can delete all message user from chat**
        `{0}cc` (username/reply user)
    **You can clear all history chat from bot**
        `{0}endchat bot`
    **You can clear all history chat from private messages**
        `{0}endchat private`
    **This command will clear all history chat from bot and private messages**
        `{0}endchat all`
    **You can clear history chat from target**
        `{0}endchat` (username/reply user)</blockquote>

<blockquote expandable>--**Chats Commands**--

    **You can create a channel with this command**
        `{0}create ch`
    **You can create a super group with this command**
        `{0}create gc`
    **You can get invite link chats**
        `{0}getlink`
    **Check total members from chat**
        `{0}cekmember`
    **Get online members from chat**
        `{0}cekonline`
    **Get total messages user from chat**
        `{0}cekmsg` (username/reply user)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("cc")
async def _(client, message):
    return await cc_cmd(client, message)


@CMD.UBOT("endchat")
async def _(client, message):
    return await endchat_cmd(client, message)


@CMD.UBOT("create")
async def _(client, message):
    return await create_cmd(client, message)


@CMD.UBOT("getlink")
@CMD.ADMIN
async def _(client, message):
    return await getlink_cmd(client, message)


@CMD.UBOT("cekmember")
async def _(client, message):
    return await cekmember_cmd(client, message)


@CMD.UBOT("cekonline")
async def _(client, message):
    return await cekonline_cmd(client, message)


@CMD.UBOT("cekmsg")
async def _(client, message):
    return await cekmsg_cmd(client, message)
