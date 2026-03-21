from pathlib import Path

from command import alfabet_cmd, toxic_cmd
from helpers import CMD

__MODULES__ = "Toxic"
__HELP__ = """<blockquote>Command Help **Toxic**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **For toxic to people**
        **`{0}ngentot` | `{0}hina` 
        `{0}ngatain` | `{0}ngaca` 
        `{0}goblok` | `{0}alay` 
        `{0}yatim` | `{0}kontol`**</blockquote>

<blockquote expandable>--**Others Commands**-- 

    **Use alphabet to toxic**
        **`{0}a` | `{0}e` | `{0}i` | `{0}m` | `{0}r` | `{0}v`
        `{0}b` | `{0}f` | `{0}j` | `{0}n` | `{0}s` | `{0}w`
        `{0}c` | `{0}g` | `{0}k` | `{0}o` | `{0}t` | `{0}x`
        `{0}d` | `{0}h` | `{0}l` | `{0}p` | `{0}u` | `{0}z`**</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("ngentot|ngatain|goblok|yatim|hina|alay|ngaca|kontol")
async def _(client, message):
    return await toxic_cmd(client, message)


@CMD.UBOT("a|b|c|d|e|f|g|h|i|j|k|l|m|o|p|r|s|t|u|v|w|x|z")
async def _(client, message):
    plugin_name = Path(__file__).stem
    print(plugin_name)
    return await alfabet_cmd(client, message)
