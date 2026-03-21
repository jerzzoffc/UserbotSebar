from command import id_cmd, infoinline_cmd, mestats_cmd
from helpers import CMD

__MODULES__ = "Info"
__HELP__ = """<blockquote>Command Help **Info**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can get information about user**
        `{0}info` (username/reply user)
    **You can get statistics your account**
        `{0}mestats`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("id")
async def _(client, message):
    return await id_cmd(client, message)


@CMD.UBOT("mestats")
async def _(client, message):
    return await mestats_cmd(client, message)


@CMD.UBOT("info")
async def _(client, message):
    return await infoinline_cmd(client, message)
