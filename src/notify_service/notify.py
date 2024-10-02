import logging
from observer_pack.models import Observer


class NotifyService(Observer):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__class__.__name__)

    async def update(self) -> None:
        self.logger.info("Start NotifyService")
        # Code for notify all users
        pass
