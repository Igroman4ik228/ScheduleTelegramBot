
from app.factory_pack.models import IBackgroundServiceFactory
from services.notify_service.notify import NotifyService
from services.parser_service.parser import ParserService


class ParserFactory(IBackgroundServiceFactory):
    def __init__(self, additional_param: list[object], time_span: int, notify: NotifyService):
        super().__init__(additional_param, time_span)
        self.notify = notify

    def get(self):
        return super().get()

    def _create(self):
        return [ParserService(self.additional_param[0], self.time_span, self.notify)]

    def _create_range(self):
        return [ParserService(param, self.time_span, self.notify) for param in self.additional_param]
