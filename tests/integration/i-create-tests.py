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


async def test_new_index_pipeline(redical):
	async with redical as pipe:
		fut1 = pipe.set('foo', 'bar')
		fut2 = pipe.ft.create(
			'myindex',
			TextField('line', TextField.SORTABLE),
			NumericField('speech', NumericField.SORTABLE),
		)
		fut3 = pipe.get('foo')
		fut4 = pipe.ft.info('myindex')

	assert True is await fut1
	assert True is await fut2
	assert 'bar' == await fut3
	info = await fut4
	assert 'myindex' == info.name
	field_defs = dict(
		line=dict(type='TEXT', options=['WEIGHT', '1', 'SORTABLE']),
		speech=dict(type='NUMERIC', options=['SORTABLE']),
	)
	assert field_defs == info.field_defs
	assert 0 == info.number_of_documents
	assert 0 == info.number_of_terms
	assert 0 == info.number_of_records
