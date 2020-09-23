import pytest  # type: ignore

from redicalsearch import GeoField, IndexExistsError, NumericField, RediSearch, TextField

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.fixture
def client(redical):
	return RediSearch('shakespeare', redis=redical)


async def test_create_index(client, redical):
	await client.create_index(
		TextField('line', TextField.SORTABLE),
		TextField('play', TextField.NO_STEM),
		NumericField('speech', NumericField.SORTABLE),
		TextField('speaker', TextField.NO_STEM),
		TextField('entry'),
		GeoField('location'),
	)
	assert 1 == await redical.exists('idx:shakespeare')


async def test_create_index_already_exists(client):
	await client.create_index(TextField('line', TextField.SORTABLE))
	with pytest.raises(IndexExistsError, match='shakespeare'):
		await client.create_index(TextField('line', TextField.SORTABLE))
