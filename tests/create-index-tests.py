import pytest  # type: ignore

from aioredisearch import GeoField, NumericField, TextField


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			(TextField('myfield'),),
			dict(max_text_fields=True),
			['FT.CREATE', 'shakespeare', 'MAXTEXTFIELDS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(temporary=5.5),
			['FT.CREATE', 'shakespeare', 'TEMPORARY', '5.5', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(no_offsets=True),
			['FT.CREATE', 'shakespeare', 'NOOFFSETS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(no_highlights=True),
			['FT.CREATE', 'shakespeare', 'NOHL', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(no_fields=True),
			['FT.CREATE', 'shakespeare', 'NOFIELDS', 'SCHEMA', 'myfield', 'TEXT']
		),
		(
			(TextField('myfield'),),
			dict(no_frequencies=True),
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
				max_text_fields=True,
				no_fields=True,
				no_frequencies=True,
				no_highlights=True,
				no_offsets=True,
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
				TextField('line', sortable=True),
				TextField('play', no_stem=True),
				NumericField('speech', sortable=True),
				TextField('speaker', no_stem=True),
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
async def test_create_index(args, kwargs, expected, redisearch):
	client = redisearch('shakespeare')
	await client.create_index(*args, **kwargs)
	client.redis.execute_command.assert_called_once_with(*expected)
