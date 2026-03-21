__MODULES__ = "Spotify"
__HELP__ = """<blockquote>Command Help **Spotify**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Download audio from spotify by title**
        `{0}spotify` (title)</blockquote>
<b>   {1}</b>
"""


from command import spotify_search
from helpers import CMD

IS_PRO = True


@CMD.UBOT("spotify")
async def _(client, message):
    return await spotify_search(client, message)
