import pytest  # type: ignore

from aioredisearch import GeoField, IndexExistsError, NumericField, RediSearch, TextField


@pytest.fixture
def client(redis):
	return RediSearch('shakespeare', redis=redis)


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
	with pytest.raises(IndexExistsError, match='shakespeare'):
		await client.create_index(TextField('line', TextField.SORTABLE))
