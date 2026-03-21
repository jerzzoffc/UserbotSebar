from command import genai_cmd
from helpers import CMD

__MODULES__ = "Genai"
__HELP__ = """<blockquote>Command Help **Genai**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate image naked girl**
        `{0}genai` (prompt)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("genai")
async def _(client, message):
    return await genai_cmd(client, message)
