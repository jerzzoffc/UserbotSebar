import asyncio
import functools
import glob
import json
import multiprocessing
import os
import random
import re
import time
import traceback
import urllib.parse
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from math import floor
from typing import Union

import aiohttp
import httpx
import yt_dlp
from pyrogram.errors import FloodPremiumWait, FloodWait
from pyrogram.types import Voice
from pytgcalls.types import AudioQuality, MediaStream, VideoQuality

from config import URL_LOGO
from logs import logger

from .tools import Tools

max_workers = multiprocessing.cpu_count() * 2
exc_ = ThreadPoolExecutor(max_workers=max_workers)

lyrical = {}
queues = {}
demus_data = {}
streaming_data = {}
downloader = {}


def cookies():
    folder_path = f"{os.getcwd()}/storage/cookies/youtube"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return f"""storage/cookies/youtube/{str(cookie_txt_file).split("/")[-1]}"""


class StreamingTools:
    play_text = """
<blockquote expandable>   <u><b><emoji id=5260268501515377807>🎼</emoji>{} Now Playing {} <emoji id={}>🎶</emoji></b></u>
<b><emoji id=5260348422266822411>🎵</emoji> Title: {}</b>
<b><emoji id=5260652149469094137>🎤</emoji> Uploader: <u>{}</u></b>
<b><emoji id=5258258882022612173>⏲️️</emoji> Duration: <code>{}</code></b>
<b><emoji id=5316727448644103237>📩</emoji> Request: {}</b></blockquote>"""

    def __init__(self):
        self.active_calls = {}
        self.queue = {}

    def sanitize_url(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        for param in ["list", "index", "start_radio", "pp"]:
            qs.pop(param, None)
        parsed = parsed._replace(query=urllib.parse.urlencode(qs, doseq=True))
        return urllib.parse.urlunparse(parsed)

    async def run_stream(self, link, media_type):
        url = self.sanitize_url(link)
        ydl_params = f"--cookies {cookies()} -f {url} --extractor-args 'youtubetab:skip=authcheck'"

        stream_kwargs = {
            "media_path": url,
            "audio_parameters": AudioQuality.STUDIO,
            "ytdlp_parameters": ydl_params,
        }

        if media_type == "Video":
            stream_kwargs["video_parameters"] = VideoQuality.HD_720p
        else:
            stream_kwargs["video_flags"] = MediaStream.Flags.IGNORE

        return MediaStream(**stream_kwargs)

    def get_active_call(self, chat_id, user_id):
        return self.active_calls.get((chat_id, user_id))

    def add_active_call(self, chat_id, user_id, group_call, message):
        self.active_calls[(chat_id, user_id)] = (group_call, message)

    def is_active_call(self, chat_id, user_id):
        call_data = self.active_calls.get((chat_id, user_id))
        if call_data:
            return True
        return False

    def remove_active_call(self, chat_id, user_id):
        if (chat_id, user_id) in self.active_calls:
            del self.active_calls[(chat_id, user_id)]

    def get_queue(self, chat_id, user_id):
        return self.queue.get((chat_id, user_id), [])

    def add_to_queue(self, chat_id, user_id, media_info):
        if (chat_id, user_id) not in self.queue:
            self.queue[(chat_id, user_id)] = []
        self.queue[(chat_id, user_id)].append(media_info)

    def clear_queue(self, chat_id, user_id):
        if (chat_id, user_id) in self.queue:
            del self.queue[(chat_id, user_id)]

    def skip(self, chat_id, user_id):
        queue = self.get_queue(chat_id, user_id)
        if not queue:
            return None
        queue.pop(0)
        return queue[0] if queue else None

    def get_current_and_next_media(self, chat_id, user_id):
        queue = self.get_queue(chat_id, user_id)
        if not queue:
            return None, []
        current_media = queue[0]
        next_media_list = queue[1:]
        return current_media, next_media_list


stream = StreamingTools()


class YoutubeAPI:
    def __init__(self):
        self.last_percent = 0
        self.regex = r"^(https:\/\/www.youtube.com\/)(.*)$"

    async def valid(self, link: str):
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def download(self, url, as_video=False):
        url = stream.sanitize_url(url)
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "cookiefile": cookies(),
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "extractor_args": {"youtubetab": "skip=authcheck"},
        }

        if as_video:
            ydl_opts["format"] = (
                "bestvideo[height<=?720][width<=?1280][ext=mp4]+bestaudio[ext=m4a]"
            )
        else:
            ydl_opts["format"] = "bestaudio[ext=m4a]"

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ytdl_data = await self.run_sync(ydl.extract_info, url, download=True)

        file_name = ydl.prepare_filename(ytdl_data)
        inpoh = "Video" if as_video else "Audio"
        videoid = ytdl_data.get("id")
        title = ytdl_data.get("title")
        url = f"https://youtu.be/{videoid}"
        duration = int(ytdl_data.get("duration", 0))
        channel = ytdl_data.get("uploader", "Unknown")
        views = f"{ytdl_data.get('view_count', 0):,}".replace(",", ".")
        thumb = f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"

        data_ytp = """
<blockquote expandable><b>   「💡 Information {}」</b>
🏷 Title: <code>{}</code>
🧭 Duration: <code>{}</code>
👀 See: <code>{}</code>
📢 Channel: <code>{}</code>
🔗 Link: <a href='{}'>Youtube</a>
⚡Downloaded By: {}</blockquote>"""
        try:
            return (
                file_name,
                inpoh,
                title,
                duration,
                views,
                channel,
                url,
                videoid,
                thumb,
                data_ytp,
            )
        except Exception:
            print(f"ERROR: {traceback.format_exc()}")

    def run_sync(self, func, *args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(
            None, functools.partial(func, *args, **kwargs)
        )

    async def progress(self, current, total, pros, mulai, operasi, nama_file):
        percent = current * 100 / total
        if (
            floor(percent) >= self.last_percent + random.randint(17, 25)
            or floor(percent) == 100
        ):
            now = time.time()
            self.last_percent = floor(percent)
            kecepatan = current / (now - mulai)
            sisa_waktu = (total - current) / kecepatan
            progress_bar = self.generate_progress_bar(floor(percent))
            teks_progress = f"""
<blockquote expandable><b> • {operasi}</b>
📂 <code>{nama_file}</code>
📊 <b>Progress</b>: {progress_bar} <code>{floor(percent)}%</code>
🚀 <b>Speed</b>: <code>{self.humanbytes(kecepatan)}/s</code>
⏳ <b>Remaining time</b>: <code>{self.human_time(sisa_waktu)}</code>
💾 <b>Downloaded</b>: <code>{self.humanbytes(current)}</code> / <code>{self.humanbytes(total)}</code></blockquote>"""
            try:
                await pros.edit(teks_progress)
                await sleep(2)
            except (FloodWait, FloodPremiumWait) as e:
                await sleep(e.value)
                await self.progress(current, total, pros, mulai, operasi, nama_file)

    def generate_progress_bar(self, percent):
        bar_length = 10
        filled_length = floor(bar_length * percent / 100)
        bar = "▰" * filled_length + "▱" * (bar_length - filled_length)
        return f"[{bar}]"

    def humanbytes(self, size):
        if not size:
            return ""
        power = 2**10
        raised_to_pow = 0
        dict_power_n = {0: "", 1: "Kb", 2: "Mb", 3: "Gb", 4: "Tb"}
        while size > power:
            size /= power
            raised_to_pow += 1
        return f"{str(round(size, 2))} {dict_power_n[raised_to_pow]}"

    def human_time(self, milliseconds: int) -> str:
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = (
            (f"{str(days)} d, " if days else "")
            + (f"{str(hours)} h, " if hours else "")
            + (f"{str(minutes)} m, " if minutes else "")
            + (f"{str(seconds)} s, " if seconds else "")
            + (f"{str(milliseconds)} ms, " if milliseconds else "")
        )
        return tmp[:-2]


youtube = YoutubeAPI()


class TelegramAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = 5

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x, disable_web_page_preview=True)
        return True

    async def get_link(self, message):
        return message.link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            file_name = file.file_name
            if file_name is None:
                file_name = "Audio Telegram" if audio else "Video Telegram"
        except Exception:
            file_name = "Audio Telegram" if audio else "Video Telegram"
        return file_name

    async def get_duration(self, filex, file_path):
        try:
            dur = Tools.seconds_to_min(filex.duration)
        except Exception:
            try:
                dur = youtube.run_sync(None, Tools.check_duration, file_path)
                dur = Tools.seconds_to_min(dur)
            except Exception:
                return "Unknown"
        return dur

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        if audio:
            try:
                file_name = (
                    audio.file_unique_id
                    + "."
                    + (
                        (audio.file_name.split(".")[-1])
                        if (not isinstance(audio, Voice))
                        else "ogg"
                    )
                )
            except:
                file_name = audio.file_unique_id + "." + ".ogg"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        if video:
            try:
                file_name = (
                    video.file_unique_id + "." + (video.file_name.split(".")[-1])
                )
            except:
                file_name = video.file_unique_id + "." + "mp4"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        return file_name

    async def download(self, client, message, pros, fname):
        try:
            left_time = {}
            speed_counter = {}
            if os.path.exists(fname):
                return True

            async def down_load():
                async def progress(current, total):
                    if current == total:
                        return
                    current_time = time.time()
                    start_time = speed_counter.get(message.id)
                    check_time = current_time - start_time
                    if datetime.now() > left_time.get(message.id):
                        percentage = current * 100 / total
                        percentage = str(round(percentage, 2))
                        speed = current / check_time
                        eta = int((total - current) / speed)
                        downloader[message.id] = eta
                        eta = Tools.get_readable_time(eta)
                        if not eta:
                            eta = "0 sec"
                        total_size = Tools.convert_bytes(total)
                        completed_size = Tools.convert_bytes(current)
                        speed = Tools.convert_bytes(speed)
                        text = f"""
**{client.me.mention} Telegram Media Downloader**

**Size:** {total_size}
**Complete:** {completed_size} 
**percentage:** {percentage[:5]}%

**Speed:** {speed}/s
**Elapsed Time:** {eta}"""
                        try:
                            await pros.edit_text(text)
                        except:
                            pass
                        left_time[message.id] = datetime.now() + timedelta(
                            seconds=self.sleep
                        )

                speed_counter[message.id] = time.time()
                left_time[message.id] = datetime.now()

                try:
                    await client.download_media(
                        message.reply_to_message,
                        file_name=fname,
                        progress=progress,
                    )
                    await pros.edit_text("**Succesfully Downloaded...**")
                    downloader.pop(message.id)
                except Exception:
                    await pros.edit_text(
                        "**Failed to download the media from the telegram.**"
                    )

            if len(downloader) > 10:
                timers = []
                for x in downloader:
                    timers.append(downloader[x])
                try:
                    low = min(timers)
                    eta = Tools.get_readable_time(low)
                except:
                    eta = "Unknown"
                await pros.edit_text(
                    "**overload ** with downloads now. \n\n ** try after: ** {} (__ The expected time__)".format(
                        eta
                    )
                )
                return False

            task = asyncio.create_task(down_load())
            lyrical[pros.id] = task
            await task
            downloaded = downloader.get(message.id)
            if downloaded:
                downloader.pop(message.id)
                return False
            verify = lyrical.get(pros.id)
            if not verify:
                return False
            lyrical.pop(pros.id)
            return True
        except Exception as er:
            logger.error(f"Error: {traceback.format_exc()}")


telegram = TelegramAPI()


async def download_thumbnail(url, file_path):
    async with httpx.AsyncClient(http2=True) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
        except Exception as e:
            logger.error(f"Error downloading thumbnail: {e}")
    return None


class YoutubeSearch:
    def __init__(self, search_terms: str, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = []

    async def _fetch(self, client, url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    async def _search(self):
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        BASE_URL = "https://www.youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"

        async with httpx.AsyncClient(http2=True) as client:
            response = await self._fetch(client, url)
            while "ytInitialData" not in response:
                response = await self._fetch(client, url)
            results = self._parse_html(response)
            if self.max_results is not None and len(results) > self.max_results:
                self.videos = results[: self.max_results]
            else:
                self.videos = results

    def _parse_html(self, response):
        results = []
        try:
            start = response.index("ytInitialData") + len("ytInitialData") + 3
            end = response.index("};", start) + 1
            json_str = response[start:end]
            data = json.loads(json_str)
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing YouTube data: {e}")
            return results

        try:
            sections = data["contents"]["twoColumnSearchResultsRenderer"][
                "primaryContents"
            ]["sectionListRenderer"]["contents"]
            for section in sections:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for video in items:
                    if "videoRenderer" not in video:
                        continue
                    video_data = video["videoRenderer"]
                    res = {
                        "id": video_data.get("videoId"),
                        "thumbnails": [
                            thumb.get("url")
                            for thumb in video_data.get("thumbnail", {}).get(
                                "thumbnails", []
                            )
                        ],
                        "title": video_data.get("title", {})
                        .get("runs", [{}])[0]
                        .get("text"),
                        "long_desc": video_data.get("descriptionSnippet", {})
                        .get("runs", [{}])[0]
                        .get("text"),
                        "channel": video_data.get("longBylineText", {})
                        .get("runs", [{}])[0]
                        .get("text"),
                        "duration": video_data.get("lengthText", {}).get("simpleText"),
                        "views": video_data.get("viewCountText", {}).get("simpleText"),
                        "publish_time": video_data.get("publishedTimeText", {}).get(
                            "simpleText"
                        ),
                        "url_suffix": video_data.get("navigationEndpoint", {})
                        .get("commandMetadata", {})
                        .get("webCommandMetadata", {})
                        .get("url"),
                    }
                    results.append(res)
        except KeyError as e:
            logger.error(f"Key error during parsing: {e}")
        return results

    async def fetch_results(self):
        await self._search()

    def to_dict(self, clear_cache=True):
        result = self.videos
        if clear_cache:
            self.videos = []
        return result

    def to_json(self, clear_cache=True):
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = []
        return result

    def get_id(self, index=0):
        return self.videos[index]["id"] if self.videos else None

    def get_link(self, index=0):
        if self.videos:
            video = self.videos[index]
            return f"https://www.youtube.com{video['url_suffix']}"
        return None

    def get_title(self, index=0):
        return self.videos[index]["title"] if self.videos else None

    async def get_thumbnail(self, index=0):
        if not self.videos or index >= len(self.videos):
            return URL_LOGO

        thumbnails = self.videos[index].get("thumbnails", [])
        if not thumbnails:
            return URL_LOGO

        thumbnail_url = thumbnails[0]

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(thumbnail_url) as response:
                    if response.status == 200:
                        path = f"downloads/thumbnail_{random.randint(1, 999999)}.jpg"
                        if os.path.exists(path):
                            path = (
                                f"downloads/thumbnail_{random.randint(1, 999999)}.jpg"
                            )
                        return await download_thumbnail(thumbnail_url, path)
            except Exception as e:
                logger.error(f"Error validating thumbnail URL: {e}")

        return URL_LOGO

    def get_clean_link(self, index=0):
        if self.videos:
            video_id = self.videos[index]["id"]
            return f"https://www.youtube.com/watch?v={video_id}"
        return None

    def get_channel(self, index=0):
        return self.videos[index]["channel"] if self.videos else None

    def get_duration(self, index=0):
        return self.videos[index]["duration"] if self.videos else None

    def get_views(self, index=0):
        return self.videos[index]["views"] if self.videos else None

    def get_publish_time(self, index=0):
        return self.videos[index]["publish_time"] if self.videos else None
