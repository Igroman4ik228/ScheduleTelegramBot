from __future__ import annotations

from typing import TYPE_CHECKING

from app.factory_pack.models import BackgroundServiceFactory
from database.cache.repositories import CacheRepositoryService
from database.db import DatabaseAlchemy
from helpers.week import Week
from services.parser_service.parser import ParserService
from services.request_service.request import RequestService

if TYPE_CHECKING:
    from services.notify_service.notify import NotifyService


class ParserFactory(BackgroundServiceFactory):
    def __init__(
        self,
        interval: int,
        urls: list[str],
        request: RequestService,
        db: DatabaseAlchemy,
        notify: NotifyService,
        cache_service: CacheRepositoryService,
    ):
        self._parsers: list[ParserService] | None = None
        self.interval = interval
        self.urls = urls
        self.request = request
        self.db = db
        self.notify = notify
        self.cache_service = cache_service

    def get(self):
        if self._parsers is None:
            self._parsers = self._create()
        return self._parsers

    def get_parser(self, global_shift: int) -> ParserService:
        for parser in self.get():
            if parser.global_shift == global_shift:
                return parser
        raise ValueError(f"Parser for global_shift {global_shift} not found")

    def get_week(self, global_shift: int) -> Week:
        return self.get_parser(global_shift).parser.week

    def _create(self) -> list[ParserService]:
        return [
            ParserService(
                url,
                global_shift,
                self.interval,
                self.request,
                self.db,
                self.cache_service,
                self.notify,
            )
            for global_shift, url in enumerate(self.urls, 1)
        ]
