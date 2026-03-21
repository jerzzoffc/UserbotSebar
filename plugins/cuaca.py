__MODULES__ = "Cuaca"
__HELP__ = """<blockquote>Command Help **Cuaca** </blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get weather information of the country**
        `{0}cuaca` (country)</blockquote>
<b>   {1}</b>
"""
IS_BASIC = True

from command import cuaca_cmd
from helpers import CMD


@CMD.UBOT("cuaca")
async def _(client, message):
    return await cuaca_cmd(client, message)
