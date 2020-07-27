import pytest  # type: ignore

from aioredisearch import (
	DocumentExists,
	GeoField,
	IndexExists,
	IndexInfo,
	NumericField,
	RediSearch,
	TextField,
	UnknownIndex,
)


@pytest.fixture
def client(redis):
	return RediSearch('shakespeare', redis=redis)


# |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
# FT.CREATE [
@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_index(client, redis):
	await client.create_index(
		TextField('line', TextField.SORTABLE),
		TextField('play', TextField.NO_STEM),
		NumericField('speech', NumericField.SORTABLE),
		TextField('speaker', TextField.NO_STEM),
		TextField('entry'),
		GeoField('location'),
	)
	exists = await redis.exists('idx:shakespeare')
	assert True is exists


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_index_already_exists(client):
	await client.create_index(TextField('line', TextField.SORTABLE))
	with pytest.raises(IndexExists, match='shakespeare'):
		await client.create_index(TextField('line', TextField.SORTABLE))
# ]


# |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
# FT.INFO [
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
async def test_info_no_index(redis):
	client = RediSearch('nonexistent', redis=redis)
	with pytest.raises(UnknownIndex, match='nonexistent'):
		await client.info()
# ]


# |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
# FT.ADD [
@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document(client, redis):
	await client.create_index(TextField('line', TextField.SORTABLE))
	await client.add_document('adocid', ('line', 'i said stuff'), ('anotherfield', 'with a value'))
	assert True is await redis.exists('adocid')
	index_info = await client.info()
	assert 1 == index_info.number_of_documents


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document_exists(client):
	await client.create_index(TextField('line', TextField.SORTABLE))
	await client.add_document('adocid', ('line', 'some lines'))
	with pytest.raises(DocumentExists, match='adocid'):
		await client.add_document('adocid', ('line', 'more lines'))
# ]
