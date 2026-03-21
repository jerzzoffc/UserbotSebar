import logging
import os
import sys
from datetime import datetime

import config


class ConnectionHandler(logging.Handler):
    def emit(self, record):
        msg = record.getMessage()
        keywords = [
            # "OSError",
            "TimeoutError",
            "socket",
            # "ConnectionResetError",
            # "ConnectionAbortedError",
        ]
        if any(k in msg for k in keywords):
            with open("log-restart.txt", "a") as f:
                f.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Restart triggered by: {msg}\n"
                )

            args = sys.argv if sys.argv else ["src.py"]
            os.execv(sys.executable, [sys.executable] + args)


logging.basicConfig(level=logging.INFO, format="%(name)s[%(levelname)s]: %(message)s")
connection_handler = ConnectionHandler()

for lib in {
    "pyrogram",
    "pytgcalls",
    "py-tgcalls",
    "aiorun",
    "asyncio",
    "hydrogram",
}:
    logging.getLogger(lib).setLevel(logging.ERROR)
    logging.getLogger(lib).addHandler(connection_handler)


logger = logging.getLogger(f"{config.BOT_NAME}")
