import pytest  # type: ignore

pytestmark = [pytest.mark.skip('new version')]


@pytest.mark.asyncio
async def test_info(mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	client.redis.execute.return_value = [
		'index_name',
		'shakespeare',
		'index_options',
		[],
		'fields',
		[['line', 'type', 'TEXT', 'SORTABLE']],
		'num_docs',
		'0',
		'num_terms',
		'0',
		'num_records',
		'0',
	]
	await client.info()
	client.redis.execute.assert_called_once_with('FT.INFO', 'shakespeare')
