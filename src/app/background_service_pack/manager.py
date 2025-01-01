import asyncio

from app.background_service_pack.builder import BackgroundBuilder


class BackgroundManager:
    def __init__(self, builder: BackgroundBuilder):
        self.services = builder.get_services()

    async def start_services(self):
        tasks = (service.active() for service in self.services)
        await asyncio.gather(*tasks)

    async def pause_services(self):
        tasks = (service.pause() for service in self.services)
        await asyncio.gather(*tasks)

    async def pause_service_by_class(self, service_class: type):
        """
        Pause all services where type = service_class

        :param service_class: Class of service for pause.
        """
        tasks = (service.pause()
                 for service in self.services if isinstance(service, service_class))
        await asyncio.gather(*tasks)

    async def active_service_by_class(self, service_class: type):
        """
        Active all services where type = service_class

        :param service_class: Class of service for actice.
        """
        tasks = (service.active()
                 for service in self.services if isinstance(service, service_class))
        await asyncio.gather(*tasks)
