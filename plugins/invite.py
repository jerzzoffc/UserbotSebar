from command import invite_cmd, inviteall_cmd
from helpers import CMD

__MODULES__ = "Invite"
__HELP__ = """<blockquote>Command Help **Invite**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can invite user or multiple user to chat**
        `{0}invite` (username) or (username1, username2)
    **You can invite all user from other chat**
        `{0}inviteall` (usernamegc)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("invite")
async def _(client, message):
    return await invite_cmd(client, message)


@CMD.UBOT("inviteall")
async def _(client, message):
    return await inviteall_cmd(client, message)
