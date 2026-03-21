from command import dalle_cmd
from helpers import CMD

__MODULES__ = "Dalle"
__HELP__ = """<blockquote>Command Help **Dalle**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate image** 
        `{0}dalle` (prompt) </blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("dalle")
async def _(client, message):
    return await dalle_cmd(client, message)
