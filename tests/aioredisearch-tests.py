from unittest import mock

import pytest  # type: ignore
from aredis import StrictRedis  # type: ignore

from aioredisearch import GeoField, NumericField, RediSearch, TagField, TextField


@pytest.fixture
def redisearch():
	def _redisearch(index_name):
		return RediSearch(index_name, redis=mock.Mock(spec=StrictRedis))
	return _redisearch


# @pytest.mark.asyncio
# async def test_create_index(redisearch):
#     client = redisearch('shakespear')
#     await client.create_index(
#         TextField('line', sortable=True),
#         TextField('play', no_stem=True),
#         NumericField('speech', sortable=True),
#         TextField('speaker', no_stem=True),
#         TextField('entry'),
#         GeoField('location')
#     )
#     expected = (
#         'FT.CREATE shakespeare SCHEMA line TEXT SORTABLE play TEXT NOSTEM speech NUMERIC SORTABLE speaker TEXT '
#         'NOSTEM entry TEXT location GEO'
#     )
#     client.redis.execute_command.assert_called_once_with(expected.split(' '))


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
		(TextField('myfield', weight=3.0), ['myfield', 'TEXT', 'WEIGHT', 3.0]),
		(TextField('myfield', no_index=True, sortable=True), ['myfield', 'TEXT', 'SORTABLE', 'NOINDEX']),
		(
			TextField('myfield', no_index=True, no_stem=True, phonetic_matcher='dm:en', sortable=True, weight=4),
			['myfield', 'TEXT', 'NOSTEM', 'WEIGHT', 4, 'PHONETIC', 'dm:en', 'SORTABLE', 'NOINDEX']
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
