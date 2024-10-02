
import logging
from observer_pack.models import Observer


class NotifyService(Observer):
    def __init__(self) -> None:
        self.logger = logging.getLogger()

    async def update(self) -> None:
        self.logger.info("Start NotifyService")
        # Code for notify all users
        pass
