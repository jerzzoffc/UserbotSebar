import asyncio
import re
from collections import defaultdict
from time import time

from unidecode import unidecode

CACHE_TTL = 300
_cache_data = {}
_cache_time = {}


class MessageFilter:
    def __init__(self):
        self.emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F"
            r"\U0001F300-\U0001F5FF"
            r"\U0001F680-\U0001F6FF"
            r"\U0001F1E0-\U0001F1FF"
            r"\U00002700-\U000027BF"
            r"\U000024C2-\U0001F251"
            "]+",
            re.UNICODE,
        )
        self.special_chars_pattern = re.compile(
            r"[^\w\s]|(\w)\1{2,}|.*\d{3,}|[^\w\s]{3,}"
        )
        self.titid_pattern = re.compile(r"\b\w+(\.\w+)+\.")
        self.one_space_pattern = re.compile(r"^(?:[A-Za-z](?:\s[A-Za-z])*)$")
        self.message_timestamps = defaultdict(list)
        self.flood_window = 1.0
        self.flood_limit = 3

    async def repeat_message(self, user_id, update):
        now = time()
        key = f"{update.chat.id}:{user_id}"
        self.message_timestamps[key] = [
            t for t in self.message_timestamps[key] if now - t < self.flood_window
        ]
        self.message_timestamps[key].append(now)
        return len(self.message_timestamps[key]) >= self.flood_limit

    def is_text_abnormal(self, text):
        txt_no_emoji = self.emoji_pattern.sub("", text)
        return (
            self.special_chars_pattern.search(text)
            or self.titid_pattern.search(text)
            or self.one_space_pattern.match(text)
            or unidecode(txt_no_emoji) != txt_no_emoji
            or text.count("\n") > 2
            or all(len(line) == 1 for line in text.split("\n") if line.strip())
        )


def url_mmk(text: str):
    pattern = (
        r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[/?]\S+)?|tg://\S+$"
    )
    return re.findall(pattern, text)


async def reply_same_type(message, mention_text=None):
    if message.photo:
        return await message.reply_photo(
            message.photo.file_id, caption=mention_text or message.caption
        )
    if message.video:
        return await message.reply_video(
            message.video.file_id, caption=mention_text or message.caption
        )
    if message.sticker:
        return await message.reply_sticker(message.sticker.file_id)
    if message.document:
        return await message.reply_document(
            message.document.file_id, caption=mention_text or message.caption
        )
    if message.audio:
        return await message.reply_audio(
            message.audio.file_id, caption=mention_text or message.caption
        )
    if message.voice:
        return await message.reply_voice(message.voice.file_id, caption=mention_text)
    if message.animation:
        return await message.reply_animation(message.animation.file_id)
    if message.location:
        return await message.reply_location(
            longitude=message.location.longitude,
            latitude=message.location.latitude,
        )
    if message.video_note:
        return await message.reply_video_note(message.video_note.file_id)


async def get_cached_list(var_func, client_id, key):
    now = asyncio.get_event_loop().time()
    cache_key = f"{client_id}:{key}"

    if cache_key in _cache_time and now - _cache_time[cache_key] < CACHE_TTL:
        return _cache_data.get(cache_key, [])

    data = await var_func(client_id, key)
    _cache_data[cache_key] = data
    _cache_time[cache_key] = now
    return data or []
