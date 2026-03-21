from command import l_t, locks_cmd, lockunlock_cmd
from helpers import CMD, Emoji

__MODULES__ = "Locks"
__HELP__ = """<blockquote>Command Help **Locks**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **To view lock type**
        `{0}locktypes`
    **View permisson from chat**
        `{0}locks`
    **You can lock some permission from chat**
        `{0}lock` (type)
    **You can unlock some permission from chat**
        `{0}unlock` (type)</blockquote>
<b>   {1}</b>
"""
IS_PRO = True


@CMD.UBOT("locktypes")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    await message.reply_text(l_t)
    return


@CMD.UBOT("lock|unlock")
async def _(client, message):
    return await lockunlock_cmd(client, message)


@CMD.UBOT("locks")
async def _(client, message):
    return await locks_cmd(client, message)
