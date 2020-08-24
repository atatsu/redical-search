import os
from unittest import mock

import pytest  # type: ignore
from aredis import StrictRedis  # type: ignore

from aioredisearch import RediSearch, TextField


@pytest.fixture
def mocked_redisearch():
	def _redisearch(index_name):
		mock_redis = mock.Mock(spec=StrictRedis)
		return RediSearch(index_name, redis=mock_redis)
	return _redisearch


# |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-
# Fixtures for integration tests only

@pytest.fixture
async def redis():
	host = os.environ.get('AIOREDISEARCH_REDIS_HOST', 'redis')
	port = os.environ.get('AIOREDISEARCH_REDIS_PORT', 6379)
	redis = StrictRedis(host=host, port=port, decode_responses=True)
	await redis.flushdb()
	yield redis
	redis.connection_pool.disconnect()


@pytest.fixture
async def client_with_index(redis):
	client = RediSearch('users', redis=redis)
	await client.create_index(
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		TextField('real_name'),
	)
	return client
