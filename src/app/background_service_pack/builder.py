from app.background_service_pack.models import BackgroundService
from services.parser_service.parser import ParserService
from services.sub_checker_service.sub_checker import SubCheckerService


class BackgroundBuilder:
    def __init__(self, parser: ParserService, sub_checker: SubCheckerService):
        self.services = [parser, sub_checker]

    def get_services(self) -> list[BackgroundService]:
        return self.services
