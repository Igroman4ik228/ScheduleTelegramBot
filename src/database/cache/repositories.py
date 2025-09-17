# from functools import wraps
# from typing import Any, Callable

# from database.cache.base import ICache
# from database.cache.serialization import AbstractSerializer, PickleSerializer

# DEFAULT_NAMESPACE = "main"


# class CacheHelper:
#     def __init__(
#         self,
#         cache: ICache,
#         serializer: AbstractSerializer = PickleSerializer(),
#     ):
#         self.cache = cache
#         self.serializer = serializer

#     async def set(
#         self,
#         key: str,
#         value: Any,
#         ttl_seconds: int,
#     ):
#         raw = self.serializer.serialize(value)
#         await self.cache.create(key, raw, ex=ttl_seconds)

#     async def get(self, key: str) -> Any | None:
#         raw = await self.cache.get(key)
#         if raw is None:
#             return None
#         return self.serializer.deserialize(raw)

#     async def delete(self, key: str | bytes):
#         await self.cache.delete(key)


# class Cacheable:
#     cache_helper: CacheHelper

#     def __init__(self, cache_helper: CacheHelper):
#         self.cache_helper = cache_helper


# def default_key_build(instance: Any, *args: Any, **kwargs: Any) -> str:
#     name = instance.__class__.__name__
#     args_str = ":".join(map(str, args))
#     kwargs_str = ":".join(
#         f"{key}={value}" for key, value in sorted(kwargs.items())
#     )
#     return f"{name}:{args_str}:{kwargs_str}"


# def cached(
#     ttl_seconds: int,
#     namespace: str = DEFAULT_NAMESPACE,
#     key_builder: Callable[..., str] = default_key_build,
# ) -> Callable:
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         async def wrapper(instance: Any, *args: Any, **kwargs: Any) -> Any:
#             helper = get_cache_helper(instance)

#             base_key = key_builder(instance, *args, **kwargs)
#             key = (
#                 f"{namespace}:{instance.__module__}:{func.__name__}:{base_key}"
#             )

#             # Попытка получить значение из кэша
#             cached_value = await helper.get(key)
#             if cached_value is not None:
#                 return cached_value

#             # Если в кэше нет, выполняем функцию
#             result = await func(instance, *args, **kwargs)

#             # Сохраняем результат в кэш
#             await helper.set(key, result, ttl_seconds)

#             return result

#         wrapper._namespace = namespace
#         wrapper._key_builder = key_builder
#         return wrapper

#     return decorator


# async def clear_cache(
#     func: Callable,
#     instance: Any,
#     *args: Any,
#     **kwargs: Any,
# ):
#     namespace = getattr(func, "_namespace", DEFAULT_NAMESPACE)
#     key_builder = getattr(func, "_key_builder", default_key_build)

#     base_key = key_builder(instance, *args, **kwargs)
#     key = f"{namespace}:{func.__module__}:{func.__name__}:{base_key}"

#     await get_cache_helper(instance).delete(key)


# def get_cache_helper(instance: Any) -> CacheHelper:
#     cache_helper: CacheHelper | None = getattr(instance, "cache_helper", None)
#     if cache_helper is None:
#         raise RuntimeError(f"Instance {instance} has no cache_helper")
#     return cache_helper
