import pytest  # type: ignore

from aioredisearch import GeoField, FieldFlags, NumericField, TagField, TextField


@pytest.mark.parametrize(
	'field,expected',
	[
		(GeoField('myfield'), ['myfield', 'GEO']),
		(GeoField('myfield', GeoField.NO_INDEX), ['myfield', 'GEO', 'NOINDEX']),
		(
			GeoField('myfield', GeoField.NO_INDEX | FieldFlags.NO_STEM | FieldFlags.SORTABLE),
			['myfield', 'GEO', 'NOINDEX'],
		)
	]
)
def test_geo_field(field, expected):
	actual = list(field)
	assert expected == actual


@pytest.mark.parametrize(
	'field,expected',
	[
		(NumericField('myfield'), ['myfield', 'NUMERIC']),
		(NumericField('myfield', NumericField.SORTABLE), ['myfield', 'NUMERIC', 'SORTABLE']),
		(NumericField('myfield', NumericField.NO_INDEX), ['myfield', 'NUMERIC', 'NOINDEX']),
		(
			NumericField('myfield', NumericField.SORTABLE | NumericField.NO_INDEX),
			['myfield', 'NUMERIC', 'SORTABLE', 'NOINDEX']
		),
		(
			NumericField('myfield', NumericField.SORTABLE | NumericField.NO_INDEX | FieldFlags.NO_STEM),
			['myfield', 'NUMERIC', 'SORTABLE', 'NOINDEX']
		),
	]
)
def test_numeric_field(field, expected):
	actual = list(field)
	assert expected == actual


@pytest.mark.parametrize(
	'field,expected',
	[
		(TagField('myfield'), ['myfield', 'TAG']),
		(TagField('myfield', separator='|'), ['myfield', 'TAG', 'SEPARATOR', '|']),
		(TagField('myfield', TagField.SORTABLE), ['myfield', 'TAG', 'SORTABLE']),
		(TagField('myfield', TagField.NO_INDEX), ['myfield', 'TAG', 'NOINDEX']),
		(
			TagField('myfield', TagField.SORTABLE | TagField.NO_INDEX, separator='*'),
			['myfield', 'TAG', 'SEPARATOR', '*', 'SORTABLE', 'NOINDEX']
		),
		(TagField('myfield', FieldFlags.NO_STEM), ['myfield', 'TAG']),
	]
)
def test_tag_field(field, expected):
	actual = list(field)
	assert expected == actual


def test_tag_field_invalid_separator():
	with pytest.raises(ValueError, match="^Separator longer than one character: 'not valid'"):
		TagField('myfield', separator='not valid')


@pytest.mark.parametrize(
	'field,expected',
	[
		(TextField('myfield'), ['myfield', 'TEXT']),
		(TextField('myfield', TextField.NO_STEM), ['myfield', 'TEXT', 'NOSTEM']),
		(TextField('myfield', TextField.SORTABLE), ['myfield', 'TEXT', 'SORTABLE']),
		(TextField('myfield', TextField.NO_INDEX), ['myfield', 'TEXT', 'NOINDEX']),
		(
			TextField('myfield', phonetic_matcher=TextField.PhoneticMatchers.ENGLISH),
			['myfield', 'TEXT', 'PHONETIC', 'dm:en']
		),
		(TextField('myfield', weight=3.0), ['myfield', 'TEXT', 'WEIGHT', 3.0]),
		(
			TextField(
				'myfield',
				TextField.SORTABLE | TextField.NO_INDEX | TextField.NO_STEM,
				weight=4,
				phonetic_matcher=TextField.PhoneticMatchers.FRENCH,
			),
			['myfield', 'TEXT', 'NOSTEM', 'WEIGHT', 4.0, 'PHONETIC', 'dm:fr', 'SORTABLE', 'NOINDEX']
		),
	]
)
def test_text_field(field, expected):
	actual = list(field)
	assert expected == actual
