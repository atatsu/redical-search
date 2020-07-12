import pytest  # type: ignore
from aioredisearch import GeoField, IndexExists, NumericField, RediSearch, TextField


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_index(redis):
	client = RediSearch('shakespeare', redis=redis)
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
async def test_create_index_already_exists(redis):
	client = RediSearch('shakespeare', redis=redis)
	await client.create_index(TextField('line', sortable=True))
	with pytest.raises(IndexExists, match='shakespeare'):
		await client.create_index(TextField('line', sortable=True))
