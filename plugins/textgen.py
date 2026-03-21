__MODULES__ = "Textgen"
__HELP__ = """<blockquote>Command Help **Text Generator**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Get help prompt command for generate image ai for maximal result**
        `{0}textgen`</blockquote>
<b>   {1}</b>
"""
IS_PRO = True


from command import textgen_cmd
from helpers import CMD


@CMD.UBOT("textgen")
async def _(client, message):
    return await textgen_cmd(client, message)
