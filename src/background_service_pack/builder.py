from email.parser import Parser
from injector import Injector, inject, singleton, Module, provider

import ad_service
from background_service_pack.models import BackgroundService


class BackgroundBuilder:
    def __init__(self, parser : Parser, ad_sender: ad_service):
        self.services = [parser, ad_sender]

    def get_services(self) -> list[BackgroundService]:
        return self.services
