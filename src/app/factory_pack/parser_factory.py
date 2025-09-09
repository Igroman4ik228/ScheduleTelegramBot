from __future__ import annotations

from typing import TYPE_CHECKING

from app.factory_pack.models import IBackgroundServiceFactory
from database.cache.repositories import CacheRepositoryService
from database.db import IDatabase
from helpers.week import Week
from services.parser_service.parser import ParserService
from services.parser_service.request import Request

if TYPE_CHECKING:
    from services.notify_service.notify import NotifyService


class ParserFactory(IBackgroundServiceFactory):
    def __init__(
        self,
        time_span: int,
        urls: list[str],
        request: Request,
        db: IDatabase,
        notify: NotifyService,
        cache_service: CacheRepositoryService,
    ):
        super().__init__(time_span)
        self.urls = urls
        self.request = request
        self.db = db
        self.notify = notify
        self.cache_service = cache_service
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
                self.request,
                self.db,
                self.cache_service,
                self.notify,
            )
            parsers.append(parser)

        return parsers
