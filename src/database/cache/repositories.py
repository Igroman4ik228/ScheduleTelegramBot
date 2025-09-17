from functools import wraps
from typing import Any, Callable

from database.cache.base import ICache
from database.cache.serialization import AbstractSerializer, PickleSerializer

DEFAULT_NAMESPACE = "main"


class CacheService:
    def __init__(
        self, cache: ICache, serializer: AbstractSerializer = PickleSerializer()
    ):
        self.cache = cache
        self.serializer = serializer

    async def set_value(
        self,
        key: str | bytes,
        value: Any,
        ttl_seconds: int,
    ):
        value = self.serializer.serialize(value)
        await self.cache.create(key, value, ex=ttl_seconds)

    async def get_value(self, key: str | bytes) -> Any | None:
        cached_value = await self.cache.get(key)
        if cached_value is None:
            return None
        return self.serializer.deserialize(cached_value)

    async def clear(self, key: str | bytes):
        await self.cache.delete(key)


class Cacheable:
    cache_service: CacheService

    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service


def default_key_build(instance: Any, *args: Any, **kwargs: Any) -> str:
    name = instance.__class__.__name__
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(
        f"{key}={value}" for key, value in sorted(kwargs.items())
    )
    return f"{name}:{args_str}:{kwargs_str}"


def cached(
    ttl_seconds: int | None = None,
    namespace: str = DEFAULT_NAMESPACE,
    key_builder: Callable[..., str] = default_key_build,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(instance: Any, *args: tuple, **kwargs: dict) -> Any:
            key = key_builder(instance, *args, **kwargs)
            key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

            cache_service = get_cached_service(instance)

            # Попытка получить значение из кэша
            cached_value = await cache_service.get_value(key)
            if cached_value is not None:
                return cached_value

            # Если в кэше нет, выполняем функцию
            result = await func(instance, *args, **kwargs)

            # Сохраняем результат в кэш
            if result is not None:
                await cache_service.set_value(
                    key,
                    result,
                    ttl_seconds,
                )

            return result

        wrapper._namespace = namespace
        wrapper._key_builder = key_builder
        return wrapper

    return decorator


async def clear_cache(
    func: Callable,
    instance: Any,
    *args: Any,
    **kwargs: Any,
):
    """Очистка кэша для конкретного метода"""
    namespace = getattr(func, "_namespace", DEFAULT_NAMESPACE)
    key_builder = getattr(func, "_key_builder", default_key_build)

    key = key_builder(instance, *args, **kwargs)
    key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

    await get_cached_service(instance).clear(key)


def get_cached_service(instance: Any) -> CacheService:
    cache_service: CacheService | None = getattr(
        instance, "cache_service", None
    )
    if cache_service is None:
        raise RuntimeError(f"Instance {instance} has no cache_service")
    return cache_service
