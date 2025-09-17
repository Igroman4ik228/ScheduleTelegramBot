# from database.cache.base import BaseRedis


# class ServiceCache(BaseRedis):
#     """
#     Cache System for any service
#     """

#     def __init__(self, current_service: object):
#         """
#         args:
#             current_service : object of owner service
#         """
#         super().__init__()
#         self.cache_name = current_service.__class__.__name__

#     async def create(self, target: int, data: str):
#         """
#         Create a record for a given target with service data
#         in redis cache under the key "{service.__class__.__name__}".
#         """
#         await super().hcreate(self.cache_name, target, data)
#         self.logger.info(
#             f"Create record for {self.cache_name} with data: {target} - {data}"
#         )

#     async def get(self, target: int):
#         """
#         Returns:
#             data for current class by target value
#         """
#         data = await super().hget(self.cache_name, target)
#         if data is None:
#             return None

#         # convert
#         try:
#             data = data.decode("utf-8")
#         except (ValueError, IndexError):
#             return None

#         return data
