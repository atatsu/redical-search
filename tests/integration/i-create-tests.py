import pytest  # type: ignore

from redicalsearch import CreateFlags, GeoField, IndexExistsError, NumericField, TextField

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_new_index(redical):
	assert True is await redical.ft.create(
		'myindex',
		TextField('line', TextField.SORTABLE),
		TextField('play', TextField.NO_STEM),
		NumericField('speech', NumericField.SORTABLE),
		TextField('speaker', TextField.NO_STEM),
		TextField('entry'), GeoField('location'),
		flags=CreateFlags.NO_HIGHLIGHTS
	)
	# TODO: use `ft.info` to assert some stats


async def test_index_already_exists(redical):
	assert True is await redical.ft.create(
		'myindex',
		TextField('line', TextField.SORTABLE),
		TextField('play', TextField.NO_STEM),
		NumericField('speech', NumericField.SORTABLE),
		TextField('speaker', TextField.NO_STEM),
		TextField('entry'), GeoField('location'),
		flags=CreateFlags.NO_HIGHLIGHTS
	)
	with pytest.raises(IndexExistsError):
		assert True is await redical.ft.create(
			'myindex',
			TextField('line', TextField.SORTABLE),
			TextField('play', TextField.NO_STEM),
			NumericField('speech', NumericField.SORTABLE),
			TextField('speaker', TextField.NO_STEM),
			TextField('entry'), GeoField('location'),
			flags=CreateFlags.NO_HIGHLIGHTS
		)
