__MODULES__ = "Clone"
__HELP__ = """<blockquote>Command Help **Clone**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Clone user profile**
        `{0}clone` (username/reply user)
    **Restore own profile**
        `{0}clone restore`</blockquote>
<b>   {1}</b>
"""


from command import clone_cmd
from helpers import CMD

IS_BASIC = True


@CMD.UBOT("clone")
async def _(_, message):
    return await clone_cmd(_, message)
