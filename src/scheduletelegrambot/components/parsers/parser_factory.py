from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scheduletelegrambot.components.parsers.parser import (
    ParserDependencies,
    ScheduleParser,
)
from scheduletelegrambot.enums import StudyShift

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
        dependencies: ParserDependencies,
    ):
        self._parsers: list[ScheduleParser] | None = None
        self.config = config
        self.dependencies = dependencies

    def get(self) -> list[ScheduleParser]:
        if self._parsers is None:
            self._parsers = self._create()
        return self._parsers

    def get_parser(self, study_shift: StudyShift) -> ScheduleParser:
        for parser in self.get():
            if parser.study_shift == study_shift:
                return parser
        raise LookupError(f"Parser for study shift {study_shift.value} was not found")

    def get_week(self, study_shift: StudyShift) -> Week:
        parser = self.get_parser(study_shift).parser
        if parser is None or parser.week is None:
            raise RuntimeError("Schedule parser has not completed its first run")
        return parser.week

    def _create(self) -> list[ScheduleParser]:
        if len(self.config.urls) != len(StudyShift):
            raise ValueError("Exactly one URL is required for every study shift")
        return [
            ScheduleParser(
                url=url,
                study_shift=study_shift,
                interval=self.config.interval,
                dependencies=self.dependencies,
            )
            for study_shift, url in zip(StudyShift, self.config.urls, strict=True)
        ]
