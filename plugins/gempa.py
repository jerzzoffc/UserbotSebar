__MODULES__ = "Gempa"
__HELP__ = """<blockquote>Command Help **Gempa**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can check information gempa today's**
        `{0}gempa`</blockquote> 
<b>   {1}</b>
"""

IS_PRO = True


from command import gempa_cmd
from helpers import CMD


@CMD.UBOT("gempa")
async def _(client, message):
    return await gempa_cmd(client, message)
