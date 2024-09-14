from email.parser import Parser
from injector import Injector, inject, singleton, Module, provider

import AdService
from BackgroundServicePack.models import BackgroundService


class BackgroundBuilder:
    def __init__(self, parser : Parser, ad_sender: AdService):
        self.services = [parser, ad_sender]

    def get_services(self) -> list[BackgroundService]:
        return self.services
