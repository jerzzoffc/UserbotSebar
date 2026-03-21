from command import (ban_cmd, del_cmd, group_cmd, kick_cmd, mute_cmd, pin_cmd,
                     promote_cmd, purge_cmd, purgeme_cmd, report_cmd,
                     staff_cmd, zombies_cmd)
from helpers import CMD

__MODULES__ = "Admins"
__HELP__ = """<blockquote>Command Help **Admins**</blockquote>
<blockquote expandable>--**Moderation Commands**--

    **Kick user from chat**
        `{0}kick` (username/reply user)
    **Kick user with delete the messages**
        `{0}delkick` (username/reply user)
        
    **Ban user from chat**    
        `{0}ban` (username/reply user)
    **Ban user with delete th messages**
        `{0}delban` (username/reply user)
    **Unban user from chat**
        `{0}unban` (username/reply user)
        
    **Mute user from chat**
        `{0}mute` (username/reply user)
    **Mute user with delete message**
        `{0}delmute` (username/reply user)
    **Unmute user from chat**
        `{0}unmute` (username/reply user)
        
    **Banned deleted account from chat**
        `{0}zombies`</blockquote>
        
<blockquote expandable>--**Management Commands**--

    **Pin the message from chat**    
        `{0}pin` (reply message) 
    **Unpin the message from chat**    
        `{0}unpin` (reply message)
        
    **Delete the message from chat**    
        `{0}del` (reply message) 
    **Delete your message from chat**    
        `{0}purgeme` (number)
    **Delete all message from chat**    
        `{0}purge` (reply message)
        
    **Add user to admins**    
        `{0}promote` (username/reply user)
    **Add user to admins with full acces**    
        `{0}fullpromote` (username/reply user)
    **Delete user from admins**    
        `{0}demote` (username/reply user)
        
    **Get admins from chat**
        `{0}staff` 
    **Change user admin title from chat**
        `{0}title` (username/reply user) (title)
    **Change description group**
        `{0}group desc` (text/reply text)
    **Change title group**
        `{0}group title` (text/reply text)
    **Change media photo group**
        `{0}group media` (text/reply text)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("staff")
@CMD.ONLY_GROUP
async def _(client, message):
    return await staff_cmd(client, message)


@CMD.UBOT("purgeme")
async def _(client, message):
    return await purgeme_cmd(client, message)


@CMD.UBOT("purge")
async def _(client, message):
    return await purge_cmd(client, message)


@CMD.UBOT("kick|delkick")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await kick_cmd(client, message)


@CMD.UBOT("ban|delban|unban")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await ban_cmd(client, message)


@CMD.UBOT("del")
async def _(client, message):
    return await del_cmd(client, message)


@CMD.UBOT("pin|unpin")
async def _(client, message):
    return await pin_cmd(client, message)


@CMD.UBOT("mute|delmute|unmute")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await mute_cmd(client, message)


@CMD.UBOT("zombies")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await zombies_cmd(client, message)


@CMD.UBOT("report")
@CMD.ONLY_GROUP
async def _(client, message):
    return await report_cmd(client, message)


@CMD.UBOT("fullpromote|promote|demote")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await promote_cmd(client, message)


@CMD.UBOT("title|group")
@CMD.ONLY_GROUP
@CMD.ADMIN
async def _(client, message):
    return await group_cmd(client, message)
