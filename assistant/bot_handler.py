import traceback

from clients import bot
from command import (add_prem_user, add_seller, addexpired_user, backup,
                     button_bot, cb_evaluasi_bot, cb_gitpull2, cb_shell,
                     cek_expired, copymsg_bot, get_prem_user, get_seles_user,
                     getid_bot, incoming_message, lapor_bug, make_pack,
                     make_stickers, mass_report, outgoing_reply,
                     remove_stickers, request_bot, restart_userbot, restore,
                     send_broadcast, send_ubot_1, send_ubot_2, set_plan,
                     setads_bot, setimg_start, sewa_expired, start_home,
                     un_prem_user, un_seller, unexpired)
from helpers import CMD
from logs import logger


@CMD.BOT(
    [
        "restart",
        "setimg",
        "referral",
        "start",
        "button",
        "id",
        "request",
        "bug",
        "setads",
        "token",
        "getubot",
        "cekubot",
        "restore",
        "backup",
        "sh",
        "shell",
        "e",
        "eval",
        "reboot",
        "update",
        "kontol",
        "close",
        "status",
        "kang",
        "unkang",
        "addprem",
        "lite",
        "basic",
        "pro",
        "addprem",
        "unprem",
        "listprem",
        "addexpired",
        "unexpired",
        "cek",
        "addseller",
        "unseller",
        "listseller",
        "broadcast",
        "setplan",
        "report",
        "addpack",
        "sewa",
    ]
)
async def _(client, message):
    try:
        command = message.command
        logger.info(f"Bot command:{command}")
        if command[0] == "setimg":
            return await setimg_start(client, message)
        elif command[0] == "start":
            return await start_home(client, message)
        elif command[0] == "restart":
            return await restart_userbot(client, message)
        elif command[0] == "button":
            return await button_bot(client, message)
        elif command[0] == "id":
            return await getid_bot(client, message)
        elif command[0] == "request":
            return await request_bot(client, message)
        elif command[0] == "bug":
            return await lapor_bug(client, message)
        elif command[0] == "setads":
            return await setads_bot(client, message)
        elif command[0] == "getubot":
            return await send_ubot_1(client, message)
        elif command[0] == "cekubot":
            return await send_ubot_2(client, message)
        elif command[0] == "restore":
            return await restore(client, message)
        elif command[0] == "backup":
            return await backup(client, message)
        elif command[0] in ["sh", "shell"]:
            return await cb_shell(client, message)
        elif command[0] in ["e", "eval"]:
            return await cb_evaluasi_bot(client, message)
        elif command[0] in ["reboot", "update", "reload"]:
            return await cb_gitpull2(client, message)
        elif command[0] == "kontol":
            return await copymsg_bot(client, message)
        elif command[0] == "kang":
            return await make_stickers(client, message)
        elif command[0] == "unkang":
            return await remove_stickers(client, message)

        elif command[0] in ["lite", "basic", "pro", "addprem"]:
            return await add_prem_user(client, message)
        elif command[0] == "unprem":
            return await un_prem_user(client, message)
        elif command[0] == "listseller":
            return await get_seles_user(client, message)
        elif command[0] == "addexpired":
            return await addexpired_user(client, message)
        elif command[0] == "cek":
            return await cek_expired(client, message)
        elif command[0] == "unexpired":
            return await unexpired(client, message)
        elif command[0] == "unseller":
            return await un_seller(client, message)
        elif command[0] == "addseller":
            return await add_seller(client, message)
        elif command[0] == "listprem":
            return await get_prem_user(client, message)
        elif command[0] == "broadcast":
            return await send_broadcast(client, message)
        elif command[0] == "report":
            return await mass_report(client, message)
        elif command[0] == "setplan":
            return await set_plan(client, message)
        elif command[0] == "addpack":
            return await make_pack(client, message)
        elif command[0] == "sewa":
            return await sewa_expired(client, message)
    except Exception:
        logger.error(f"Error command bot: {traceback.format_exc()}")


@CMD.CHAT_FORWARD("OUTGOING", bot)
async def _(client, message):
    return await outgoing_reply(client, message)


@CMD.CHAT_FORWARD("INCOMING", bot)
async def _(client, message):
    return await incoming_message(client, message)
