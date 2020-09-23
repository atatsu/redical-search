import os
from unittest import mock

import pytest

from redical import create_redical_pool, Redical
from redicalsearch import RediSearch, TextField


@pytest.fixture
def mocked_redisearch():
	def _redisearch(index_name):
		mock_redis = mock.Mock(spec=Redical, execute=mock.AsyncMock())
		return RediSearch(index_name, redis=mock_redis)
	return _redisearch


@pytest.fixture
def redis_uri():
	redis_uri = os.environ['REDICALSEARCH_REDIS_URI']
	return redis_uri


# |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-
# Fixtures for integration tests only

@pytest.fixture
async def redical(redis_uri):
	redical = await create_redical_pool(redis_uri)
	await redical.flushdb()
	yield redical
	redical.close()
	await redical.wait_closed()


@pytest.fixture
async def client_with_index(redical):
	client = RediSearch('users', redis=redical)
	await client.create_index(
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		TextField('real_name'),
	)
	return client
