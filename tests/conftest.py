import os
from unittest import mock

import pytest  # type: ignore
from aredis import StrictRedis  # type: ignore

from aioredisearch import RediSearch


@pytest.fixture
def redisearch():
	def _redisearch(index_name):
		return RediSearch(index_name, redis=mock.Mock(spec=StrictRedis))
	return _redisearch


@pytest.fixture
async def redis():
	host = os.environ.get('AIOREDISEARCH_REDIS_HOST', 'redis')
	port = os.environ.get('AIOREDISEARCH_REDIS_PORT', 6379)
	redis = StrictRedis(host=host, port=port, decode_responses=True)
	await redis.flushdb()
	yield redis
	redis.connection_pool.disconnect()
