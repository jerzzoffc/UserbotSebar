from command import ignore_cmd
from helpers import CMD

__MODULES__ = "Ignore"

__HELP__ = """
<blockquote>Command Help **Ignore**</blockquote>
<blockquote expandable>--**Basic Commands**--
    **You can disable plugins if you want**
        `{0}ignore` (name plugins)
    **You can enable plugins if you want**
        `{0}reignore` (name plugins)
    **You can view disabled plugins**
        `{0}ignored`</blockquote>
        
<blockquote expandable>--**Sudo Commands**--

    **You can disable plugins for sudo users**
        `{0}ignore sudo` (name plugins)
    **You can enable plugins for sudo users**
        `{0}reignore sudo` (name plugins)
    **You can view disabled plugins for sudo users**
        `{0}ignored sudo`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("ignore|reignore|ignored")
async def _(client, message):
    return await ignore_cmd(client, message)
