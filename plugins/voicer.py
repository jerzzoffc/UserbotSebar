from command import stt_cmd, tts_cmd, vremover_cmd
from helpers import CMD

__MODULES__ = "Voice"
__HELP__ = """<blockquote>Command Help **Voice**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can convert text to voice**
        `{0}tts` (text/reply text)
    **You can convert text from voice**
        `{0}stt` (reply audio)
    **You can extract instruments from media**
        `{0}vremover` (reply audio)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


@CMD.UBOT("vremover")
async def _(client, message):
    return await vremover_cmd(client, message)


@CMD.UBOT("tts")
async def _(client, message):
    return await tts_cmd(client, message)


@CMD.UBOT("stt")
async def _(client, message):
    return await stt_cmd(client, message)
