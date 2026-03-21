from command import lang_cmd, setlang_cmd, tr_cmd
from helpers import CMD

__MODULES__ = "Translate"
__HELP__ = """<blockquote>Command Help **Translate**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Translate message to other language**
        `{0}tr` (text/reply text)
    **Set default language for translate**
        `{0}setlang` (lang code)
    **You can view list language code country**
        `{0}lang`</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("tr")
async def _(client, message):
    return await tr_cmd(client, message)


@CMD.UBOT("lang")
async def _(client, message):
    return await lang_cmd(client, message)


@CMD.UBOT("setlang")
async def _(client, message):
    return await setlang_cmd(client, message)
