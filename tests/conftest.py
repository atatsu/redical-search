import os

import pytest  # type: ignore
from aredis import StrictRedis  # type: ignore


@pytest.fixture
async def redis():
	host = os.environ.get('AIOREDISEARCH_REDIS_HOST', 'redis')
	port = os.environ.get('AIOREDISEARCH_REDIS_PORT', 6379)
	redis = StrictRedis(host=host, port=port, decode_responses=True)
	await redis.flushdb()
	yield redis
	redis.connection_pool.disconnect()
