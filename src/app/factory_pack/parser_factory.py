from __future__ import annotations

from typing import TYPE_CHECKING

from app.factory_pack.models import IBackgroundServiceFactory
from helpers.week import Week
from services.parser_service.parser import ParserService
from services.sender_service.sender import SenderService

if TYPE_CHECKING:
    from services.notify_service.notify import NotifyService


class ParserFactory(IBackgroundServiceFactory):
    def __init__(
        self,
        time_span: int,
        notify: NotifyService,
        urls: list[str],
        sender: SenderService,
    ):
        super().__init__(time_span)
        self.notify = notify
        self.urls = urls
        self.sender = sender
        self.parsers: list[ParserService] = self._create()

    def get(self):
        return self.parsers

    def get_parser(self, global_shift: int) -> ParserService:
        for parser in self.parsers:
            if getattr(parser, "global_shift", None) == global_shift:
                return parser

        raise ValueError(f"Парсер для смены {global_shift} не найден.")

    def get_week(self, global_shift: int) -> Week:
        return self.get_parser(global_shift).parser.week

    def _create(self) -> list[ParserService]:
        parsers = []
        for global_shift, url in enumerate(self.urls, 1):
            parser = ParserService(
                url,
                global_shift,
                self.time_span,
                self.notify,
                self.sender,
            )
            parsers.append(parser)

        return parsers
