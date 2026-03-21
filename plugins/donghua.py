from command import donghua_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Donghua"
__HELP__ = """<blockquote>Command Help **Donghua**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get news update Donghua**
        `{0}donghua`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("donghua")
async def _(_, message):
    return await donghua_cmd(_, message)
