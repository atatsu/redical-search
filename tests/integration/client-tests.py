import pytest  # type: ignore
from aioredisearch import DocumentExists, GeoField, IndexExists, NumericField, RediSearch, TextField


@pytest.fixture
def client(redis):
	return RediSearch('shakespeare', redis=redis)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_index(client, redis):
	await client.create_index(
		TextField('line', sortable=True),
		TextField('play', no_stem=True),
		NumericField('speech', sortable=True),
		TextField('speaker', no_stem=True),
		TextField('entry'),
		GeoField('location'),
	)
	exists = await redis.exists('idx:shakespeare')
	assert True is exists


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_index_already_exists(client):
	await client.create_index(TextField('line', sortable=True))
	with pytest.raises(IndexExists, match='shakespeare'):
		await client.create_index(TextField('line', sortable=True))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document(client, redis):
	await client.create_index(TextField('line', sortable=True))
	await client.add_document('adocid', ('line', 'i said stuff'), ('anotherfield', 'with a value'))
	assert True is await redis.exists('adocid')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document_exists(client):
	await client.create_index(TextField('line', sortable=True))
	await client.add_document('adocid', ('line', 'some lines'))
	with pytest.raises(DocumentExists, match='adocid'):
		await client.add_document('adocid', ('line', 'more lines'))
