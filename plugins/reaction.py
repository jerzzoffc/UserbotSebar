from command import react2_cmd, react_cmd
from helpers import CMD

__MODULES__ = "Reaction"
__HELP__ = """<blockquote>Command Help **Reaction** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **Give reactions to chat with costum emoji or random**
        `{0}react` (chatid) (emoji/random)
    **Give many reactions to 1 message with active userbot**
        `{0}react2` (reply message) (emoji/random)
    **Stop task reaction with taskid**
        `{0}cancel` (taskid)
        </blockquote>
<b>   {1}</b>
"""
IS_PRO = True


@CMD.UBOT("react")
@CMD.FAKEDEV("react")
@CMD.DEV_CMD("react")
async def _(client, message):
    return await react_cmd(client, message)


@CMD.UBOT("react2")
@CMD.FAKEDEV("react2")
@CMD.DEV_CMD("react2")
async def _(client, message):
    return await react2_cmd(client, message)
