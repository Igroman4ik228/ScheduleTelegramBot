from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import BaseModel


class UoW:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self, *instances: BaseModel):
        self.session.add_all(instances)
        await self.session.commit()

    async def merge(self, *instances: BaseModel):
        for instance in instances:
            await self.session.merge(instance)

    async def delete(self, *instances: BaseModel):
        for instance in instances:
            await self.session.delete(instance)
        await self.session.commit()
