import asyncio

from pyrogram.types import InlineKeyboardMarkup

from clients import navy
from config import BOT_NAME, HELPABLE, USENAME_OWNER
from database import dB
from helpers import paginate_modules


async def auto_delete_message(client, chat_id, message_id, delay=300):
    try:
        await asyncio.sleep(delay)
        await dB.remove_var(chat_id, "is_bot_pro")
        await dB.remove_var(chat_id, "is_bot")
        await dB.remove_var(chat_id, "is_bot_basic")
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Auto delete message error: {e}")


async def general_plugins(client, message):
    user_id = message.from_user.id
    text = message.text
    split_plan = text.split()[2]
    plan_map = {
        "🧩 Plan Basic": {
            "is_pro": False,
            "is_basic": True,
            "filter_func": lambda name, data: not data.get("is_pro", False),
            "remove_pro": True,
        },
        "⚡ Plan Lite": {
            "is_pro": False,
            "is_basic": False,
            "filter_func": lambda name, data: not data.get("is_pro", False)
            and not data.get("is_basic", False),
            "remove_pro": True,
        },
        "💎 Plan Pro": {
            "is_pro": True,
            "is_basic": False,
            "filter_func": lambda name, data: True,
            "remove_pro": False,
        },
    }

    plan = plan_map[text]
    visible_helpable = {
        name: data for name, data in HELPABLE.items() if plan["filter_func"](name, data)
    }

    prefix = navy.get_prefix(user_id)
    text_help = (
        await dB.get_var(user_id, "text_help")
        or f"**🤖 {BOT_NAME} by {USENAME_OWNER}**"
    )
    full = f"<a href=tg://user?id={user_id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a>"

    msg = f"""<b>
Inline Help
    Plan: <b>{split_plan}</b>
    Prefixes: <code>{' '.join(prefix)}</code>
    Plugins: <code>{len(visible_helpable)}</code>
    {full} </b>
<blockquote>{text_help}</blockquote>"""

    await dB.set_var(message.chat.id, "is_bot", True)

    if plan["is_pro"]:
        await dB.set_var(message.chat.id, "is_bot_pro", True)
    else:
        await dB.remove_var(message.chat.id, "is_bot_pro")

    if plan["is_basic"]:
        await dB.set_var(message.chat.id, "is_bot_basic", True)
    else:
        await dB.remove_var(message.chat.id, "is_bot_basic")

    sent_msg = await message.reply(
        msg,
        reply_markup=InlineKeyboardMarkup(
            paginate_modules(0, visible_helpable, "help", is_bot=True)
        ),
    )
    asyncio.create_task(
        auto_delete_message(client, message.chat.id, sent_msg.id, delay=120)
    )
    return sent_msg
