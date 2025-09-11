import asyncio

from app.background_service_pack.builder import BackgroundBuilder


class BackgroundManager:
    def __init__(self, builder: BackgroundBuilder):
        self.services = builder.get_services()

    async def start_services(self):
        await asyncio.gather(*(s.start() for s in self.services))

    async def pause_services(self):
        await asyncio.gather(*(s.pause() for s in self.services))

    async def stop_services(self):
        await asyncio.gather(*(s.stop() for s in self.services))

    async def start_service_by_class(self, service_class: type):
        await asyncio.gather(
            *(s.start() for s in self.services if isinstance(s, service_class))
        )

    async def pause_service_by_class(self, service_class: type):
        await asyncio.gather(
            *(s.pause() for s in self.services if isinstance(s, service_class))
        )

    async def stop_service_by_class(self, service_class: type):
        await asyncio.gather(
            *(s.stop() for s in self.services if isinstance(s, service_class))
        )
