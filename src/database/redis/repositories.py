from datetime import timedelta
from functools import wraps
from typing import Any, Callable

from database.redis.base import redis_client
from database.redis.serialization import AbstractSerializer, PickleSerializer

DEFAULT_TTL = 10


def build_key_from_repo(instance: Any, *args: tuple, **kwargs: dict) -> str:
    """Генерация ключа на основе модели и аргументов репозитория."""
    repo_name = instance.__class__.__name__
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(f"{key}={value}" for key,
                          value in sorted(kwargs.items()))
    return f"{repo_name}:{args_str}:{kwargs_str}"


async def set_redis_value(
    key: bytes | str,
    value: bytes | str,
    ttl: int | timedelta | None = DEFAULT_TTL,
    is_transaction: bool = False
) -> None:
    """Сохранение значения в Redis с возможностью задания TTL."""
    async with redis_client.pipeline(transaction=is_transaction) as pipeline:
        await pipeline.set(key, value)
        if ttl:
            await pipeline.expire(key, ttl)
        await pipeline.execute()


def cached(
    ttl: int | timedelta = DEFAULT_TTL,
    namespace: str = "repo_cache",
    key_builder: Callable[..., str] = build_key_from_repo,
    serializer: AbstractSerializer | None = None,
    cache=redis_client
) -> Callable:
    """Декоратор для кэширования результатов методов репозиториев."""
    if serializer is None:
        serializer = PickleSerializer()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(instance: Any, *args: tuple, **kwargs: dict) -> Any:
            key = key_builder(instance, *args, **kwargs)
            key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

            # Попытка получить значение из кэша
            cached_value = await cache.get(key)
            if cached_value is not None:
                return serializer.deserialize(cached_value)

            # Если в кэше нет, выполняем функцию
            result = await func(instance, *args, **kwargs)

            # Сохраняем результат в кэш
            await set_redis_value(
                key=key,
                value=serializer.serialize(result),
                ttl=ttl,
            )

            return result

        return wrapper

    return decorator


async def clear_cache(
    func: Callable,
    instance: Any,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Очистка кэша для конкретного метода и аргументов."""
    namespace: str = kwargs.get("namespace", "repo_cache")
    key = build_key_from_repo(instance, *args, **kwargs)
    key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"

    await redis_client.delete(key)
