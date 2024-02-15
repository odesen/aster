from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode

from fastapi import Request
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

CacheKeyBuilder = Callable[[Request], str]


def default_cache_key_builder(request: Request) -> str:
    query_params: list[tuple[str, Any]] = list(request.query_params.items())
    query_params.sort(key=lambda x: x[0])
    return request.url.path + urlencode(query_params, doseq=True)


class RedisCache:
    def __init__(
        self,
        redis_url: str,
        default_expiration: int = 60,
        cache_key_builder: CacheKeyBuilder = default_cache_key_builder,
    ) -> None:
        self._redis = Redis(connection_pool=ConnectionPool.from_url(redis_url))
        self.default_expiration = default_expiration
        self.key_builder = cache_key_builder

    async def get(self, key: str) -> bytes | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, expiration: int | None = None) -> None:
        await self._redis.set(key, value, ex=expiration)

    async def delete(self, key: str) -> Any:
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(key) == 1

    async def close(self) -> None:
        await self._redis.close()

    def build_cache_key(self, request: Request, cache_key_builder: CacheKeyBuilder | None) -> str:
        key_builder = cache_key_builder or self.key_builder
        return key_builder(request)
