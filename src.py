import asyncio

from aiorun import run, shutdown_waits_for
from pyrogram.errors import (AuthKeyDuplicated, AuthKeyUnregistered,
                             SessionRevoked, UserAlreadyParticipant,
                             UserDeactivated, UserDeactivatedBan)

from clients import UserBot, bot, navy
from config import (BLACKLIST_KATA, LOG_SELLER, OWNER_ID, WAJIB_JOIN,
                    costum_font)
from database import dB
from helpers import (AutoBC, AutoFW, CheckUsers, ExpiredSewa, ExpiredUser,
                     ReadUser, installPeer, monitor, stop_main)
from logs import logger

list_error = []


async def monitoring():
    logger.info("=== INFORMASI SISTEM ===")
    system_info = monitor.get_system_info()
    logger.info(f"CPU Total: {system_info['CPU_TOTAL']} cores")
    logger.info(f"CPU Usage: {system_info['CPU_USAGE']:.2f}%")
    logger.info(f"RAM Total: {monitor.format_bytes(system_info['RAM_TOTAL'])}")
    logger.info(
        f"RAM Usage: {monitor.format_bytes(system_info['RAM_USAGE'])} ({system_info['RAM_PERCENT']:.2f}%)"
    )

    def print_monitoring_data(data):
        cpu_usage = data["system_info"]["CPU_USAGE"]
        ram_percent = data["system_info"]["RAM_PERCENT"]
        logger.info(f"CPU: {cpu_usage:.1f}% | RAM: {ram_percent:.1f}%")

    await monitor.start(interval=5, callback=print_monitoring_data)


async def cleanup_total(ubot_id):
    """Clean up database records for a specific userbot."""
    try:
        await dB.remove_ubot(ubot_id)
        logger.info(f"Deleted user {ubot_id}")
    except Exception as e:
        logger.error(f"Failed to cleanup userbot {ubot_id}: {e}")


async def handle_start_error():
    if list_error:
        for data in list_error:
            ubot = data["user"]
            reason = data["error_msg"]
            await bot.send_message(
                LOG_SELLER,
                f"<b>Userbot {ubot} failed to start due to {reason}, deleted user on database</b>",
            )
            try:
                await bot.send_message(
                    int(ubot), f"<b>Userbot anda telah dihapus karna {reason}.</b>"
                )
            except Exception:
                pass
            await cleanup_total(ubot)


async def start_ubot(ubot):
    """Start a userbot instance and handle setup."""
    userbot = UserBot(**ubot)
    try:
        await userbot.start()
        for chat in WAJIB_JOIN:
            try:
                await userbot.join_chat(chat)
            except UserAlreadyParticipant:
                pass
            except Exception:
                continue
    except (AuthKeyUnregistered, AuthKeyDuplicated, SessionRevoked):
        reason = "Session Ended"
        data = {"user": int(ubot["name"]), "error_msg": reason}
        list_error.append(data)
    except (UserDeactivated, UserDeactivatedBan):
        reason = "Account Banned by Telegram"
        data = {"user": int(ubot["name"]), "error_msg": reason}
        list_error.append(data)


async def start_main_bot():
    """Start the main bot after userbots."""
    logger.info("🤖 Starting main bot...")
    await bot.start()
    await bot.add_reseller()
    logger.info("✅ Main bot started successfully.")
    total_bots = len(navy._ubot)
    message = "🔥**Bot berhasil diaktifkan**🔥\n" f"✅ **Total User: {total_bots}**"
    await dB.set_var(bot.id, "total_users", total_bots)
    try:
        await bot.send_message(OWNER_ID, f"<blockquote>{message}</blockquote>")
    except Exception:
        pass


async def start_userbots():
    logger.info("🔄 Starting userbots...")
    userbots = await dB.get_userbots()
    sem = asyncio.Semaphore(10)

    async def safe_start(ubot):
        async with sem:
            await start_ubot(ubot)

    tasks = [asyncio.create_task(safe_start(ubot)) for ubot in userbots]
    await asyncio.gather(*tasks)
    logger.info(f"✅ All {len(userbots)} userbots started successfully.")


async def start_task():
    tasks = [
        AutoBC(),
        ReadUser(),
        AutoFW(),
        ExpiredUser(),
        ExpiredSewa(),
        installPeer(),
        CheckUsers(),
    ]
    for task in tasks:
        asyncio.create_task(task)
    logger.info(f"✅ Started task {len(tasks)}.")


async def main():
    for a in costum_font:
        BLACKLIST_KATA.append(a)
    try:
        await dB.initialize()
        await start_userbots()
        await start_main_bot()
        await handle_start_error()
        await start_task()
    except KeyboardInterrupt:
        logger.warning("Forced stop… Bye!")


async def shutdown_callback(loop=None):
    try:
        if loop and loop.is_closed():
            logger.warning("Event loop sudah ditutup.")
            return
        await shutdown_waits_for(stop_main())
    except asyncio.CancelledError:
        logger.warning("Stopped All.")
    except Exception as e:
        logger.error(f"❌ Error saat shutdown: {e}")


if __name__ == "__main__":
    run(
        main(),
        loop=bot.loop,
        shutdown_callback=shutdown_callback,
    )
