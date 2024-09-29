
from logging import Logger
from observer_pack.models import Observer


class NotifyService(Observer):
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    async def update(self) -> None:
        self.logger.info("Start NotifyService")
        # Code for notify all users
        pass
