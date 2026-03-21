from command import inline_cmd
from helpers import CMD

__MODULES__ = "Alive"
__HELP__ = """<blockquote>Command Help **Alive**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **View status bot**
        `{0}alive`</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("alive")
async def _(client, message):
    return await inline_cmd(client, message)
