__MODULES__ = "Apk"
__HELP__ = """<blockquote>Command Help **Apk**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search apk from an1.com site**
        `{0}an1` (query)

    **Search apk from apkmoddy site**
        `{0}moddy` (query)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


from command import apkan1_cmd, apkmoddy_cmd
from helpers import CMD


@CMD.UBOT("an1")
async def _(client, message):
    return await apkan1_cmd(client, message)


@CMD.UBOT("moddy")
async def _(client, message):
    return await apkmoddy_cmd(client, message)
