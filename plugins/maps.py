from command import maps_cmd
from helpers import CMD

__MODULES__ = "Maps"
__HELP__ = """<blockquote>Command Help **Maps**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get rute for location** 
        `{0}maps` (addres) </blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("gps|maps")
async def _(client, message):
    return await maps_cmd(client, message)
