
from app.factory_pack.models import IBackgroundServiceFactory
from services.notify_service.notify import NotifyService
from services.parser_service.parser import ParserService


class ParserFactory(IBackgroundServiceFactory):
    def __init__(self, time_span: int, notify: NotifyService, *args: object):
        super().__init__(time_span, *args)
        self.notify = notify

    def get(self):
        return super().get()

    def _create(self):
        return [ParserService(param, self.time_span, self.notify) for param in self.args]
