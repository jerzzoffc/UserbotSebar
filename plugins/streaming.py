from clients import navy
from command import (channelplay_cmd, end_cmd, group_call_ends, pause_cmd,
                     play_cmd, playlist_cmd, resume_cmd, skip_cmd, volume_cmd)
from helpers import CMD

__MODULES__ = "Music"
__HELP__ = """<blockquote>Command Help **Music**</blockquote>
<blockquote expandable>--**Basic Commands**--
    **Use `v` for play video**
        `{0}play` (title)
        `{0}vplay` (title)
    **Resume playing**
        `{0}resume`
    **Pause playing**
        `{0}pause`
    **Skip playing**
        `{0}skip`
    **End playing**
        `{0}end`</blockquote>
        
<blockquote expandable>--**Channels Commands**--
    **Playing to channel, use `v` for playing video**
        `{0}cplay` (title) 
        `{0}cvplay` title
    **Resume playing channel**
        `{0}cresume`
    **Pause playing channel**
        `{0}cpause`
    **Skip playing channel**
        `{0}cskip`
    **End playing channel**
        `{0}cend`
    **Linked channel to chat**
        `{0}channelplay linked`
    **Disable linked channel**
        `{0}channelplay disable`
    **Check linked playback channel**
        `{0}channelplay status`</blockquote>
    
<blockquote expandable>--**Other Commands**--
    **Set volume playing, then try leave voice chat and join again**
        `{0}volume` (1-200)
    **Get playlist playing now**
        `{0}playlist`</blockquote>
<b>   {1}</b>"""

IS_PRO = True


@navy.group_call_logs()
async def _(client, update):
    return await group_call_ends(client, update)


@CMD.UBOT("play|vplay|cplay|cvplay")
async def _(client, message):
    return await play_cmd(client, message)


@CMD.UBOT("resume|cresume")
async def _(client, message):
    return await resume_cmd(client, message)


@CMD.UBOT("end|cend")
async def _(client, message):
    return await end_cmd(client, message)


@CMD.UBOT("pause|cpause")
async def _(client, message):
    return await pause_cmd(client, message)


@CMD.UBOT("skip|cskip")
async def _(client, message):
    return await skip_cmd(client, message)


@CMD.UBOT("playlist|cplaylist")
async def _(client, message):
    return await playlist_cmd(client, message)


@CMD.UBOT("volume|cvolume")
async def _(client, message):
    return await volume_cmd(client, message)


@CMD.UBOT("channelplay")
async def _(client, message):
    return await channelplay_cmd(client, message)
