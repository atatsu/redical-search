from unittest import mock

import pytest  # type: ignore

from redical import RedicalPipeline
from redicalsearch import RediSearch


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			{},
			['FT.ADD', 'shakespeare', 'adocid', 1.0, 'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'],
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(score=5),
			['FT.ADD', 'shakespeare', 'adocid', 1.0, 'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'],
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(no_save=True),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'NOSAVE',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.DEFAULT),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'REPLACE',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.PARTIAL),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'REPLACE', 'PARTIAL',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.NO_CREATE),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'REPLACE', 'NOCREATE',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.NO_CREATE | RediSearch.ReplaceOptions.PARTIAL),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'REPLACE', 'PARTIAL', 'NOCREATE',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(language=RediSearch.Languages.RUSSIAN),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'LANGUAGE', 'russian',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(payload='asdf'),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'PAYLOAD', 'asdf',
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace_condition='@timestamp < 23323234234'),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'IF', "'@timestamp < 23323234234'",
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(
				language=RediSearch.Languages.SWEDISH,
				no_save=True,
				payload='asdf',
				replace=RediSearch.ReplaceOptions.NO_CREATE | RediSearch.ReplaceOptions.PARTIAL,
				replace_condition='@timestamp < 23323234234',
				score=5.5,
			),
			[
				'FT.ADD', 'shakespeare', 'adocid', 1.0, 'NOSAVE', 'REPLACE', 'PARTIAL', 'NOCREATE',
				'LANGUAGE', 'swedish', 'PAYLOAD', 'asdf', 'IF', "'@timestamp < 23323234234'",
				'FIELDS', 'foo', 'bar baz', 'bar', 'baz', 'baz', '1234'
			]
		),
	]
)
async def test_add_document(args, kwargs, expected, mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	await client.add_document(*args, **kwargs)
	client.redis.execute.assert_called_once_with(*expected)


@pytest.mark.asyncio
async def test_add_document_no_fields(mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	with pytest.raises(ValueError, match='Field/value pairs must be supplied'):
		await client.add_document('adocid')


@pytest.fixture
def mock_pipeline():
	pipeline = mock.Mock(spec=RedicalPipeline)
	# pipeline.__aenter__ = mock.AsyncMock(return_value=pipeline)
	# pipeline.__aexit__ = mock.AsyncMock(return_value=False)
	return pipeline


@pytest.fixture
def mock_client_pipeline(mocked_redisearch, mock_pipeline):
	def _redisearch(index_name):
		client = mocked_redisearch(index_name)
		client.redis.__aenter__ = mock.AsyncMock(return_value=mock_pipeline)
		client.redis.__aexit__ = mock.AsyncMock(return_value=False)
		return client
	return _redisearch


# Pipelining

@pytest.mark.skip('get rid of pipeline batch stuff')
@pytest.mark.asyncio
async def test_default_batch(mock_client_pipeline, mock_pipeline):
	client = mock_client_pipeline('shakespeare')
	async with client.add_document.batch() as add:
		await add('adocid1', *dict(foo='bar', bar='baz').items())
		await add('adocid2', *dict(foo='bar', bar='baz').items())
		await add('adocid3', *dict(foo='bar', bar='baz').items())
		mock_pipeline.execute.assert_has_calls([
			mock.call('FT.ADD', 'shakespeare', 'adocid1', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
			mock.call('FT.ADD', 'shakespeare', 'adocid2', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
			mock.call('FT.ADD', 'shakespeare', 'adocid3', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
		])
		mock_pipeline.execute.assert_not_called()
	mock_pipeline.execute.assert_called_once_with()


@pytest.mark.skip('get rid of pipeline batch stuff')
@pytest.mark.asyncio
async def test_batch_size(mock_client_pipeline, mock_pipeline):
	client = mock_client_pipeline('shakespeare')
	async with client.add_document.batch(size=1)as add:
		await add('adocid1', *dict(foo='bar', bar='baz').items())
		await add('adocid2', *dict(foo='bar', bar='baz').items())
		await add('adocid3', *dict(foo='bar', bar='baz').items())
		mock_pipeline.execute.assert_has_calls([
			mock.call('FT.ADD', 'shakespeare', 'adocid1', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
			mock.call('FT.ADD', 'shakespeare', 'adocid2', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
			mock.call('FT.ADD', 'shakespeare', 'adocid3', 1.0, 'FIELDS', 'foo', 'bar', 'bar', 'baz'),
		])
		mock_pipeline.execute.assert_has_calls([
			mock.call(), mock.call(), mock.call()
		])
		mock_pipeline.reset_mock()
	mock_pipeline.assert_not_called()
