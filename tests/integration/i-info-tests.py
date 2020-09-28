import pytest  # type: ignore

from redicalsearch import IndexInfo, NumericField, TextField, UnknownIndexError

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_info(redical):
	await redical.ft.create('myindex', TextField('line', TextField.SORTABLE), NumericField('page', NumericField.SORTABLE))
	info = await redical.ft.info('myindex')
	assert isinstance(info, IndexInfo)
	assert 'myindex' == info.name
	assert [] == info.options
	field_defs = dict(
		line=dict(type='TEXT', options=['WEIGHT', '1', 'SORTABLE']),
		page=dict(type='NUMERIC', options=['SORTABLE']),
	)
	assert field_defs == info.field_defs
	assert 0 == info.number_of_documents
	assert 0 == info.number_of_terms
	assert 0 == info.number_of_records


async def test_info_no_index(redical):
	with pytest.raises(UnknownIndexError):
		await redical.ft.info('nonexistent')
