from command import artiname_cmd, tafsir_cmd, zodiak_cmd
from helpers import CMD

__MODULES__ = "Primbon"
__HELP__ = """<blockquote>Command Help **Primbon**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search primbon for arti nama**
        `{0}artinama` (question)
    **Search primbon for tafsir mimpi**
        `{0}artimimpi` (question)
    **Search primbon for zodiak**
        `{0}zodiak` (query)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


@CMD.UBOT("artinama|nama")
async def _(client, message):
    return await artiname_cmd(client, message)


@CMD.UBOT("artimimpi|mimpi")
async def _(client, message):
    return await tafsir_cmd(client, message)


@CMD.UBOT("zodiak|zodiac")
async def _(client, message):
    return await zodiak_cmd(client, message)
