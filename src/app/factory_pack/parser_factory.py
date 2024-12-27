
from app.factory_pack.models import IBackgroundServiceFactory
from services.notify_service.notify import NotifyService
from services.parser_service.parser import ParserService


class ParserFactory(IBackgroundServiceFactory):
    def __init__(self, time_span: int, notify: NotifyService, urls: list[str]):
        super().__init__(time_span)
        self.notify = notify
        self.urls = urls

    def get(self):
        return super().get()

    def _create(self):
        return [ParserService(url, self.time_span, self.notify) for url in self.urls]
