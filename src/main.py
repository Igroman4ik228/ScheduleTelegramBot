import asyncio
from logging import getLogger
from logging.config import dictConfig

from bot.bot import BotManager
from config import settings

dictConfig(settings.logger_conf)
logger = getLogger(__name__)


async def main() -> None:
    bot_manager = BotManager(settings.BOT_TOKEN)

    await asyncio.gather(bot_manager.start())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
