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
		prefixes=('user:',),
	)
	day = timedelta(days=1).total_seconds()
	async with redical as pipe:
		pipe.hset(
			'user:1',
			username='arenthop',
			joined=joined + day,
			location='-3.9264,57.5243',
			password_hash='secret1',
			avatar='avatar1',
			phrase='hello world'
		)
		pipe.hset(
			'user:2',
			username='pethroul',
			joined=joined + day * 2,
			location='55.584,54.4435',
			password_hash='secret2',
			avatar='avatar2',
			phrase='world hello'
		)
		pipe.hset(
			'user:3',
			username='cobiumet',
			joined=joined + day * 3,
			location='23.7275,37.9838',
			password_hash='secret3',
			avatar='avatar3',
			phrase='hello'
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


async def test_basic_search_pipeline(client):
	async with client as pipe:
		fut1 = pipe.set('foo', 'bar')
		fut2 = pipe.ft.search('user', '@username:arenthop')
		fut3 = pipe.get('foo')

	assert True is await fut1
	results = await fut2
	assert 1 == results.total
	assert 1 == results.count
	assert 0 == results.offset
	assert 0 == results.limit
	assert isinstance(results.documents[0], DocumentWrap)
	assert isinstance(results.documents[0].document, dict)
	assert 'bar' == await fut3


async def test_basic_search_model_pipeline(client):
	class MyDocument(Document):
		username: str
		joined: datetime
		phrase: str

	async with client as pipe:
		fut1 = pipe.set('foo', 'bar')
		fut2 = pipe.ft.search('user', '@username:arenthop', document_cls=MyDocument)
		fut3 = pipe.get('foo')

	assert True is await fut1
	results = await fut2
	assert results.count > 0
	assert isinstance(results.documents[0].document, MyDocument), type(results.documents[0].document)
	assert 'arenthop' == results.documents[0].document.username
	assert 'bar' == await fut3
