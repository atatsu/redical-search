from datetime import datetime, timedelta, timezone

import pytest  # type: ignore

from aioredisearch import Document, DocumentWrap, GeoField, NumericField, RediSearch, SearchResult, TextField


@pytest.fixture
def joined():
	week = timedelta(days=7).total_seconds()
	joined = datetime.now(timezone.utc).timestamp() - week
	return joined


@pytest.fixture
async def client(redis, joined):
	client = RediSearch('users', redis=redis)
	await client.create_index(
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		NumericField('joined', NumericField.SORTABLE),
		GeoField('location'),
		TextField('password_hash', TextField.NO_STEM),
		TextField('phrase'),
	)
	day = timedelta(days=1).total_seconds()
	async with client.add_document.batch() as add:
		await add(
			'user1',
			*dict(
				username='arenthop', joined=joined + day, location='-3.9264,57.5243', password_hash='secret1',
				avatar='avatar1', phrase='hello world',
			).items()
		)
		await add(
			'user2',
			*dict(
				username='pethroul', joined=joined + day * 2, location='55.584,54.4435', password_hash='secret2',
				avatar='avatar2', phrase='world hello',
			).items(),
		)
		await add(
			'user3',
			*dict(
				username='cobiumet', joined=joined + day * 3, location='23.7275,37.9838', password_hash='secret3',
				avatar='avatar3', phrase='hello',
			).items(),
		)
	return client


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
	results = await client.search(query, **kwargs)
	assert isinstance(results, SearchResult)
	assert expected_total == results.total
	assert expected_count == results.count
	assert expected_offset == results.offset
	assert expected_limit == results.limit
	assert isinstance(results.documents[0], DocumentWrap)
	assert isinstance(results.documents[0].document, dict)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cleanup_document_cls(client, joined):
	days = timedelta(days=4).total_seconds()
	results = await client.search(f'(@joined:[{joined} {joined + days}])')
	for entry in results.documents:
		assert '_document_cls' not in entry.document


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_search_model(client, joined):
	class MyDocument(Document):
		username: str
		joined: datetime
		phrase: str

	days = timedelta(days=4).total_seconds()
	results = await client.search(
		f'(@joined:[{joined} {joined + days}])',
		document_cls=MyDocument,
		flags=client.SearchFlags.ASC,
		sort_by='username',
	)
	assert isinstance(results.documents[0].document, MyDocument), type(results.documents[0].document)
	assert results.documents[0].document.username == 'arenthop'
