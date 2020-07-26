from datetime import datetime, timedelta, timezone

import pytest  # type: ignore

from aioredisearch import GeoField, NumericField, RediSearch, SearchResult, TextField


@pytest.fixture
def joined():
	week = timedelta(days=7).total_seconds()
	joined = datetime.now(timezone.utc).timestamp() - week
	return joined


@pytest.fixture
async def client(redis, joined):
	client = RediSearch('users', redis=redis)
	await client.create_index(
		TextField('username', sortable=True, no_stem=True),
		NumericField('joined', sortable=True),
		GeoField('location'),
		TextField('password_hash', no_stem=True),
		TextField('phrase'),
	)
	day = timedelta(days=1).total_seconds()
	# FIXME: Update to pipeline usage when implemented
	await client.add_document(
		'user1',
		*dict(
			username='arenthop', joined=joined + day, location='-3.9264,57.5243', password_hash='secret1',
			avatar='avatar1', phrase='hello world',
		).items()
	)
	await client.add_document(
		'user2',
		*dict(
			username='pethroul', joined=joined + day * 2, location='55.584,54.4435', password_hash='secret2',
			avatar='avatar2', phrase='world hello',
		).items(),
	)
	await client.add_document(
		'user3',
		*dict(
			username='cobiumet', joined=joined + day * 3, location='23.7275,37.9838', password_hash='secret3',
			avatar='avatar3', phrase='hello',
		).items(),
	)
	return client


# @pytest.mark.integration
# @pytest.mark.asyncio
# async def test_basic_search(client, joined):
#     pytest.fail('boo')
#     # result = await client.search('arenthop')
#     days = timedelta(days=4).total_seconds()
#     result = await client.search(f'@joined:[{joined} {joined + days}]')
#     print(result)
#     assert isinstance(result, SearchResult)
#     assert 3 == result.total
#     assert 3 == result.count
#     assert 0 == result.limit
#     assert 0 == result.offset
#     # result = await client.search('(@username:pethroul)(@password_hash:secret2)')
#     # result = await client.search('hello world')


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
	'query,kwargs,expected_total,expected_count,expected_offset,expected_limit',
	[
		('(@username:arenthop|pethroul|cobiumet)', {}, 3, 3, 0, 0),
		('(@username:arenthop|pethroul|cobiumet)', dict(limit=(1, 2)), 3, 2, 1, 2),
	],
)
async def test_basic_search(query, kwargs, expected_total, expected_count, expected_offset, expected_limit, client):
	result = await client.search(query, **kwargs)
	assert isinstance(result, SearchResult)
	assert expected_total == result.total
	assert expected_count == result.count
	assert expected_offset == result.offset
	assert expected_limit == result.limit
