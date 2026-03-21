from command import autoread_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Autoread"
__HELP__ = """<blockquote>Command Help **Autoread**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **This command for autoread group messages**
        `{0}autoread group on`
        `{0}autoread group off`
    **This command for autoread private messages**
        `{0}autoread private on`
        `{0}autoread private off`
    **This command for autoread channel messages**
        `{0}autoread channel on`
        `{0}autoread channel off`

    **This command for autoread bot messages**
        `{0}autoread bot on`
        `{0}autoread bot off`
    **This command for autoread tagged messages**
        `{0}autoread tag on`
        `{0}autoread tag off`
    **This command for autoread all messages**
        `{0}autoread all on`
        `{0}autoread all off`
        
    **This command for settings autoread time**
        `{0}autoread time 3600`
    **Check status for autoread**
        `{0}autoread status`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("autoread")
async def _(client, message):
    return await autoread_cmd(client, message)
