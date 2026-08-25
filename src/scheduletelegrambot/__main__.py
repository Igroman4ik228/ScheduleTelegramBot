import asyncio
from contextlib import suppress

from scheduletelegrambot.app.application import Application
from scheduletelegrambot.container import create_container
from scheduletelegrambot.utils.logger import LOGGER_CONFIG, logger_configure


async def run() -> None:
    logger_configure(LOGGER_CONFIG)

    async with create_container() as container:
        application = await container.get(Application)
        application.configure(container)

        async with application:
            await application.start()


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(run())


if __name__ == "__main__":
    main()
