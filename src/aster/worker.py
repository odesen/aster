import asyncio
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings

from aster.config import get_settings


async def task1(ctx: Any) -> int:
    print("running the task")
    return 42


async def main() -> None:
    redis_url = get_settings().redis_url
    if redis_url is None:
        raise ValueError
    redis = await create_pool(
        RedisSettings(
            host=redis_url.host or "localhost",
            port=int(redis_url.port) if redis_url.port else 6379,
            username=redis_url.user,
            password=redis_url.password,
        )
    )
    job = await redis.enqueue_job("task1")
    if job:
        print(await job.result(timeout=5))


class WorkerSettings:
    functions = [task1]


if __name__ == "__main__":
    asyncio.run(main())
