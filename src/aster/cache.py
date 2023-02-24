import redis.asyncio as aioredis

from aster.config import get_settings

redis = aioredis.from_url(url=get_settings().redis_url)
