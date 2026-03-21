__MODULES__ = "Youtube"
__HELP__ = """<blockquote>Command Help **Youtube**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Download audio from youtube by title**
        `{0}song` (title)
    **Download video from youtube by title**
        `{0}vsong` (title)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


from command import youtube_search
from helpers import CMD


@CMD.UBOT("vsong|song")
async def _(client, message):
    return await youtube_search(client, message)
