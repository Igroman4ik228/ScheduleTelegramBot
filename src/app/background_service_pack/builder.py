from email.parser import Parser

from app.background_service_pack.models import BackgroundService


class BackgroundBuilder:
    def __init__(self, parser: Parser):
        self.services = [parser]

    def get_services(self) -> list[BackgroundService]:
        return self.services
