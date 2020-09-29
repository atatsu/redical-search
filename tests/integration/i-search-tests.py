from datetime import datetime, timedelta, timezone

import pytest  # type: ignore

from redicalsearch import (
	Document, DocumentWrap, GeoField, NumericField, SearchFlags, SearchResult, TextField,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.fixture
def joined():
	week = timedelta(days=7).total_seconds()
	joined = datetime.now(timezone.utc).timestamp() - week
	return joined


@pytest.fixture
async def client(redical, joined):
	await redical.ft.create(
		'user',
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		NumericField('joined', NumericField.SORTABLE),
		GeoField('location'),
		TextField('password_hash', TextField.NO_STEM),
		TextField('phrase'),
		prefix='user:',
	)
	day = timedelta(days=1).total_seconds()
	async with redical as pipe:
		pipe.hset(
			'user:1',
			'username',
			'arenthop',
			*dict(
				joined=joined + day,
				location='-3.9264,57.5243',
				password_hash='secret1',
				avatar='avatar1',
				phrase='hello world'
			).items()
		)
		pipe.hset(
			'user:2',
			'username',
			'pethroul',
			*dict(
				joined=joined + day * 2,
				location='55.584,54.4435',
				password_hash='secret2',
				avatar='avatar2',
				phrase='world hello'
			).items()
		)
		pipe.hset(
			'user:3',
			'username',
			'cobiumet',
			*dict(
				joined=joined + day * 3,
				location='23.7275,37.9838',
				password_hash='secret3',
				avatar='avatar3',
				phrase='hello'
			).items()
		)
		fut = pipe.ft.info('user')
	info = await fut
	assert 3 == info.number_of_documents
	return redical


@pytest.mark.parametrize(
	'query,kwargs,expected_total,expected_count,expected_offset,expected_limit',
	[
		('(@username:arenthop|pethroul|cobiumet)', {}, 3, 3, 0, 0),
		('(@username:arenthop|pethroul|cobiumet)', dict(limit=(1, 2)), 3, 2, 1, 2),
	],
)
async def test_basic_search(query, kwargs, expected_total, expected_count, expected_offset, expected_limit, client):
	results = await client.ft.search('user', query, **kwargs)
	assert isinstance(results, SearchResult)
	assert expected_total == results.total
	assert expected_count == results.count
	assert expected_offset == results.offset
	assert expected_limit == results.limit
	assert isinstance(results.documents[0], DocumentWrap)
	assert isinstance(results.documents[0].document, dict)


async def test_cleanup_document_cls(client, joined):
	days = timedelta(days=4).total_seconds()
	results = await client.ft.search('user', f'(@joined:[{joined} {joined + days}])')
	for entry in results.documents:
		assert '_document_cls' not in entry.document


async def test_basic_search_model(client, joined):
	class MyDocument(Document):
		username: str
		joined: datetime
		phrase: str

	days = timedelta(days=4).total_seconds()
	results = await client.ft.search(
		'user',
		f'(@joined:[{joined} {joined + days}])',
		document_cls=MyDocument,
		flags=SearchFlags.ASC,
		sort_by='username',
	)
	assert results.count > 0
	assert isinstance(results.documents[0].document, MyDocument), type(results.documents[0].document)
	assert results.documents[0].document.username == 'arenthop'
