import pytest  # type: ignore

from aioredisearch import GeoField, NumericField, RediSearch, TextField


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			(TextField('myfield'),),
			dict(flags=RediSearch.CreateFlags.MAX_TEXT_FIELDS),
			['FT.CREATE', 'shakespeare', 'MAXTEXTFIELDS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(temporary=5.5),
			['FT.CREATE', 'shakespeare', 'TEMPORARY', '5.5', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(flags=RediSearch.CreateFlags.NO_OFFSETS),
			['FT.CREATE', 'shakespeare', 'NOOFFSETS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(flags=RediSearch.CreateFlags.NO_HIGHLIGHTS),
			['FT.CREATE', 'shakespeare', 'NOHL', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(flags=RediSearch.CreateFlags.NO_FIELDS),
			['FT.CREATE', 'shakespeare', 'NOFIELDS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(flags=RediSearch.CreateFlags.NO_FREQUENCIES),
			['FT.CREATE', 'shakespeare', 'NOFREQS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(stopwords=('one', 'two', 'three')),
			['FT.CREATE', 'shakespeare', 'STOPWORDS', '3', 'one', 'two', 'three', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(stopwords=()),
			['FT.CREATE', 'shakespeare', 'STOPWORDS', '0', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(
				flags=RediSearch.CreateFlags.MAX_TEXT_FIELDS
				| RediSearch.CreateFlags.NO_FIELDS  # noqa:W503
				| RediSearch.CreateFlags.NO_FREQUENCIES  # noqa:W503
				| RediSearch.CreateFlags.NO_HIGHLIGHTS  # noqa:W503
				| RediSearch.CreateFlags.NO_OFFSETS,  # noqa:W503
				stopwords=['one'],
				temporary=3
			),
			[
				'FT.CREATE', 'shakespeare', 'MAXTEXTFIELDS', 'TEMPORARY', '3', 'NOOFFSETS', 'NOHL', 'NOFIELDS',
				'NOFREQS', 'STOPWORDS', '1', 'one', 'SCHEMA', 'myfield', 'TEXT'
			]
		),
		(
			(
				TextField('line', TextField.SORTABLE),
				TextField('play', TextField.NO_STEM),
				NumericField('speech', TextField.SORTABLE),
				TextField('speaker', TextField.NO_STEM),
				TextField('entry'),
				GeoField('location')
			),
			dict(),
			[
				'FT.CREATE', 'shakespeare', 'SCHEMA', 'line', 'TEXT', 'SORTABLE', 'play', 'TEXT', 'NOSTEM', 'speech',
				'NUMERIC', 'SORTABLE', 'speaker', 'TEXT', 'NOSTEM', 'entry', 'TEXT', 'location', 'GEO'
			]
		),
	]
)
async def test_create_index(args, kwargs, expected, mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	await client.create_index(*args, **kwargs)
	client.redis.execute_command.assert_called_once_with(*expected)
