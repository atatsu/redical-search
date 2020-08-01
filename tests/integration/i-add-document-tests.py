import pytest  # type: ignore
from aredis import ResponseError  # type: ignore

from aioredisearch import DocumentExistsError, GeoField, NumericField, RediSearch, TextField


@pytest.fixture
async def client(redis):
	client = RediSearch('users', redis=redis)
	await client.create_index(
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		NumericField('joined', NumericField.SORTABLE),
		GeoField('location'),
	)
	return client


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document(client, redis):
	await client.add_document('adocid', *dict(username='arenthop', joined=123).items())
	assert True is await redis.exists('adocid')
	index_info = await client.info()
	assert 1 == index_info.number_of_documents


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_document_exists(client):
	await client.add_document('adocid', *dict(username='arenthop', joined=123).items())
	with pytest.raises(DocumentExistsError, match='adocid'):
		await client.add_document('adocid', *dict(username='arenthop', joined=123).items())


# Pipelining

@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_document_exists_context_body(client, redis):
	try:
		async with client.add_document.batch(size=2) as add:
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid2', *dict(username='pethroul', joined=123).items())
	except ResponseError as ex:
		if 'document already exists' in str(ex).lower():
			pytest.fail('duplicate document errors should be suppressed')
		raise
	assert True is await redis.exists('adocid2')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_document_exists_context_exit(client, redis):
	try:
		async with client.add_document.batch() as add:
			await add('adocid2', *dict(username='pethroul', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
	except ResponseError as ex:
		if 'document already exists' in str(ex).lower():
			pytest.fail('duplicate document errors should be suppressed in the exit block')
		raise
	assert True is await redis.exists('adocid1')
	assert True is await redis.exists('adocid2')
