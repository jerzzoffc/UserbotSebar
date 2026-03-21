__MODULES__ = "MetaAi"
__HELP__ = """<blockquote>Command Help **MetaAi**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer question to MetaAi** 
        `{0}metaai` (question) 
    **You can answer about image to MetaAi ai** 
        `{0}metaai` (prompt)</blockquote>
<b>   {1}</b>
"""

from command import metaai_cmd
from helpers import CMD

IS_PRO = True


@CMD.UBOT("metaai")
async def _(client, message):
    return await metaai_cmd(client, message)
