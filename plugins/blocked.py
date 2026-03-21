__MODULES__ = "Blocked"
__HELP__ = """<blockquote>Command Help **Blocked**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Unblock all users**
        `{0}unblockall`
    **Get blocked users**
        `{0}blocked`</blockquote>
<b>   {1}</b>
"""


from command import blocked_cmd
from helpers import CMD

IS_BASIC = True


@CMD.UBOT("unblockall|blocked")
async def _(client, message):
    return await blocked_cmd(client, message)
