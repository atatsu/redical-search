import pytest  # type: ignore

from redicalsearch import DocumentExistsError, GeoField, NumericField, RediSearch, TextField
# FIXME: This error is a stub
from redicalsearch.exception import ResponseError

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.fixture
async def client(redical):
	client = RediSearch('users', redis=redical)
	await client.create_index(
		TextField('username', TextField.SORTABLE | TextField.NO_STEM),
		NumericField('joined', NumericField.SORTABLE),
		GeoField('location'),
	)
	return client


async def test_add_document(client, redical):
	await client.add_document('adocid', *dict(username='arenthop', joined=123).items())
	assert 1 == await redical.exists('adocid')
	index_info = await client.info()
	assert 1 == index_info.number_of_documents


async def test_add_document_exists(client):
	await client.add_document('adocid', *dict(username='arenthop', joined=123).items())
	with pytest.raises(DocumentExistsError, match='adocid'):
		await client.add_document('adocid', *dict(username='arenthop', joined=123).items())


# Pipelining

@pytest.mark.skip('get rid of pipeline batch stuff')
async def test_batch_document_exists_context_body(client, redical):
	try:
		async with client.add_document.batch(size=2) as add:
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid2', *dict(username='pethroul', joined=123).items())
	except ResponseError as ex:
		if 'document already exists' in str(ex).lower():
			pytest.fail('duplicate document errors should be suppressed')
		raise
	assert 1 == await redical.exists('adocid2')


@pytest.mark.skip('get rid of pipeline batch stuff')
async def test_batch_document_exists_context_exit(client, redical):
	try:
		async with client.add_document.batch() as add:
			await add('adocid2', *dict(username='pethroul', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
			await add('adocid1', *dict(username='arenthop', joined=123).items())
	except ResponseError as ex:
		if 'document already exists' in str(ex).lower():
			pytest.fail('duplicate document errors should be suppressed in the exit block')
		raise
	assert 1 == await redical.exists('adocid1')
	assert 1 == await redical.exists('adocid2')
