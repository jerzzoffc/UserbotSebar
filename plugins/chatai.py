from command import ask_cmd
from helpers import CMD

__MODULES__ = "ChatAI"
__HELP__ = """<blockquote>Command Help **ChatAI**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer to ai**
        `{0}ask` (prompt)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("ask|ai")
async def _(client, message):
    return await ask_cmd(client, message)
