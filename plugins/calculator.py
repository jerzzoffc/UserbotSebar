__MODULES__ = "Calculator"
__HELP__ = """<blockquote>Command Help **Calculator**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get inline calculator**
        `{0}calc`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


from command import kalkulator_cmd
from helpers import CMD


@CMD.UBOT("calc|kalkulator")
async def _(client, message):
    return await kalkulator_cmd(client, message)
