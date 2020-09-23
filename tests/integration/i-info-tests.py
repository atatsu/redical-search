import pytest  # type: ignore

from redicalsearch import IndexInfo, NumericField, RediSearch, TextField, UnknownIndexError


@pytest.fixture
def client(redical):
	return RediSearch('shakespeare', redis=redical)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_info(client):
	await client.create_index(TextField('line', TextField.SORTABLE), NumericField('page', NumericField.SORTABLE))
	info = await client.info()
	assert isinstance(info, IndexInfo)
	assert 'shakespeare' == info.name
	assert [] == info.options
	field_defs = dict(
		line=dict(type='TEXT', options=['WEIGHT', '1', 'SORTABLE']),
		page=dict(type='NUMERIC', options=['SORTABLE']),
	)
	assert field_defs == info.field_defs
	assert 0 == info.number_of_documents
	assert 0 == info.number_of_terms
	assert 0 == info.number_of_records


@pytest.mark.integration
@pytest.mark.asyncio
async def test_info_no_index(redical):
	client = RediSearch('nonexistent', redis=redical)
	with pytest.raises(UnknownIndexError, match='nonexistent'):
		await client.info()
