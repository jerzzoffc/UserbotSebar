from command import listsurah_cmd, quran_cmd
from helpers import CMD

__MODULES__ = "Qur'an"
__HELP__ = """<blockquote>Command Help **Qur'an**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get information from surah, like audio, qory, place and story of surah**
        `{0}surat` (name)
    **View all name surah**
        `{0}listsurah`</blockquote>
<b>   {1}</b>"""

IS_BASIC = True


@CMD.UBOT("listsurah")
async def _(client, message):
    return await listsurah_cmd(client, message)


@CMD.UBOT("surat|surah|quran")
async def _(client, message):
    return await quran_cmd(client, message)
