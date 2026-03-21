import traceback

from pyrogram.helpers import ikb
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from clients import bot
from config import URL_LOGO
from helpers import ButtonUtils

user_calc_data = {}

dict_calc = {
    "(",
    ")",
    "KLOS",
    "AC",
    "DEL",
    "%",
    "/",
    "*",
    "-",
    "+",
    "00",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ".",
    "=",
}


def button_calc():
    return ikb(
        [
            [("(", "calculatorcb_("), (")", "calculatorcb_)")],
            [
                ("%", "calculatorcb_%"),
                ("AC", "calculatorcb_AC"),
                ("DEL", "calculatorcb_DEL"),
                ("÷", "calculatorcb_/"),
            ],
            [
                ("7", "calculatorcb_7"),
                ("8", "calculatorcb_8"),
                ("9", "calculatorcb_9"),
                ("x", "calculatorcb_*"),
            ],
            [
                ("4", "calculatorcb_4"),
                ("5", "calculatorcb_5"),
                ("6", "calculatorcb_6"),
                ("-", "calculatorcb_-"),
            ],
            [
                ("1", "calculatorcb_1"),
                ("2", "calculatorcb_2"),
                ("3", "calculatorcb_3"),
                ("+", "calculatorcb_+"),
            ],
            [
                ("00", "calculatorcb_00"),
                ("0", "calculatorcb_0"),
                ("=", "calculatorcb_="),
                (".", "calculatorcb_."),
            ],
            [("❌ Close", "close calculator")],
        ]
    )


async def kalkulator_cmd(client, message):
    try:
        await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"calculator",
        )
    except Exception:
        await message.reply_text("<b>Cannot send inline in this chat.</b>")


async def inline_calculator(result, _):
    msg = "**Inline Calculator**"
    result.append(
        InlineQueryResultArticle(
            title="Inline Calculator",
            description="Get calculator inline mode",
            thumb_url=URL_LOGO,
            reply_markup=button_calc(),
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return result


async def calculator_callback(_, callback):
    user_id = callback.from_user.id
    query = callback.data.split("_", 1)[1]
    caption = "**Inline Calculator**"
    reply_markup = button_calc()

    data = user_calc_data.get(user_id, [])

    if query not in dict_calc:
        return await callback.answer(f"Query: {query} not found!", show_alert=True)

    if query == "DEL":
        if data:
            data = data[:-1]
    elif query == "AC":
        data = []
    elif query == "=":
        try:
            expression = "".join(data).replace("×", "*").replace("÷", "/")
            result = str(eval(expression))
            display = "".join(data)
            data = [result]
            user_calc_data[user_id] = data
            return await callback.edit_message_text(
                f"{caption}\n\n<blockquote>{display} = {result}</blockquote>",
                reply_markup=reply_markup,
            )
        except Exception as e:
            user_calc_data[user_id] = []
            print(f"Error in calculator: {traceback.format_exc()}")
            return await callback.answer(f"Error: {e}", show_alert=True)
    else:
        data.append(query)

    user_calc_data[user_id] = data
    display = "".join(data) or "0"
    await callback.edit_message_text(
        f"{caption}\n\n<blockquote>{display}</blockquote>", reply_markup=reply_markup
    )
