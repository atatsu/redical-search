from unittest import mock

import pytest  # type: ignore
from aredis import StrictRedis  # type: ignore

from aioredisearch import GeoField, NumericField, RediSearch, TagField, TextField


@pytest.fixture
def redisearch():
	def _redisearch(index_name):
		return RediSearch(index_name, redis=mock.Mock(spec=StrictRedis))
	return _redisearch


@pytest.mark.parametrize(
	'field,expected',
	[
		(GeoField('myfield'), ['myfield', 'GEO']),
		(GeoField('myfield', sortable=True), ['myfield', 'GEO', 'SORTABLE']),
		(GeoField('myfield', no_index=True, sortable=True), ['myfield', 'GEO', 'SORTABLE', 'NOINDEX']),
	]
)
def test_geo_field(field, expected):
	actual = list(field)
	assert expected == actual


def test_geo_field_nonsortable_noindex():
	with pytest.raises(ValueError, match='^Fields must be sortable or be indexed$'):
		GeoField('myfield', no_index=True)


@pytest.mark.parametrize(
	'field,expected',
	[
		(NumericField('myfield'), ['myfield', 'NUMERIC']),
		(NumericField('myfield', sortable=True), ['myfield', 'NUMERIC', 'SORTABLE']),
		(NumericField('myfield', no_index=True, sortable=True), ['myfield', 'NUMERIC', 'SORTABLE', 'NOINDEX']),
	]
)
def test_numeric_field(field, expected):
	actual = list(field)
	assert expected == actual


def test_numeric_field_nonsortable_noindex():
	with pytest.raises(ValueError, match='^Fields must be sortable or be indexed$'):
		NumericField('myfield', no_index=True)


@pytest.mark.parametrize(
	'field,expected',
	[
		(TagField('myfield'), ['myfield', 'TAG']),
		(TagField('myfield', separator='|'), ['myfield', 'TAG', 'SEPARATOR', '|']),
		(TagField('myfield', sortable=True), ['myfield', 'TAG', 'SORTABLE']),
		(TagField('myfield', no_index=True, sortable=True), ['myfield', 'TAG', 'SORTABLE', 'NOINDEX']),
		(
			TagField('myfield', no_index=True, separator='*', sortable=True),
			['myfield', 'TAG', 'SEPARATOR', '*', 'SORTABLE', 'NOINDEX']
		),
	]
)
def test_tag_field(field, expected):
	actual = list(field)
	assert expected == actual


def test_tag_field_invalid_separator():
	with pytest.raises(ValueError, match="^Separator longer than one character: 'not valid'"):
		TagField('myfield', separator='not valid')


def test_tag_field_nonsortable_noindex():
	with pytest.raises(ValueError, match='^Fields must be sortable or be indexed$'):
		TagField('myfield', no_index=True)


@pytest.mark.parametrize(
	'field,expected',
	[
		(TextField('myfield'), ['myfield', 'TEXT']),
		(TextField('myfield', no_stem=True), ['myfield', 'TEXT', 'NOSTEM']),
		(TextField('myfield', phonetic_matcher='dm:en'), ['myfield', 'TEXT', 'PHONETIC', 'dm:en']),
		(TextField('myfield', sortable=True), ['myfield', 'TEXT', 'SORTABLE']),
		(TextField('myfield', weight=3.0), ['myfield', 'TEXT', 'WEIGHT', '3.0']),
		(TextField('myfield', no_index=True, sortable=True), ['myfield', 'TEXT', 'SORTABLE', 'NOINDEX']),
		(
			TextField('myfield', no_index=True, no_stem=True, phonetic_matcher='dm:en', sortable=True, weight=4),
			['myfield', 'TEXT', 'NOSTEM', 'WEIGHT', '4', 'PHONETIC', 'dm:en', 'SORTABLE', 'NOINDEX']
		),
	]
)
def test_text_field(field, expected):
	actual = list(field)
	assert expected == actual


def test_text_field_invalid_phonetic():
	with pytest.raises(ValueError, match="^Invalid phonetic matcher: 'not valid'$"):
		TextField('myfield', phonetic_matcher='not valid')


def test_text_field_nonsortable_noindex():
	with pytest.raises(ValueError, match='^Fields must be sortable or be indexed$'):
		TextField('myfield', no_index=True)


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
