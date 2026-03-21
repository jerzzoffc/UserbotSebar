try:
    import asyncio

    import uvloop

    from logs import logger

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("🚀 UvLoop successfully setup Globaly.")
except Exception:
    logger.error("❌ Failed setup UvLoop")


from .clients import BaseClient, Bot, UserBot, bot, navy
