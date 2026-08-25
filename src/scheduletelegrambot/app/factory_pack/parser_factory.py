from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scheduletelegrambot.services.parser_service.parser import (
    ParserService,
    ParserServiceDependencies,
)

if TYPE_CHECKING:
    from scheduletelegrambot.helpers.week import Week


@dataclass(frozen=True)
class ParserFactoryConfig:
    interval: int
    urls: list[str]


class ParserFactory:
    def __init__(
        self,
        config: ParserFactoryConfig,
        dependencies: ParserServiceDependencies,
    ):
        self._parsers: list[ParserService] | None = None
        self.config = config
        self.dependencies = dependencies

    def get(self) -> list[ParserService]:
        if self._parsers is None:
            self._parsers = self._create()
        return self._parsers

    def get_parser(self, global_shift: int) -> ParserService:
        for parser in self.get():
            if parser.global_shift == global_shift:
                return parser
        raise LookupError(f"Parser for global shift {global_shift} was not found")

    def get_week(self, global_shift: int) -> Week:
        parser = self.get_parser(global_shift).parser
        if parser is None or parser.week is None:
            raise RuntimeError("Schedule parser has not completed its first run")
        return parser.week

    def _create(self) -> list[ParserService]:
        return [
            ParserService(
                url=url,
                global_shift=global_shift,
                interval=self.config.interval,
                dependencies=self.dependencies,
            )
            for global_shift, url in enumerate(self.config.urls, 1)
        ]
