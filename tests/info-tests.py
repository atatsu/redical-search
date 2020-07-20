import pytest  # type: ignore


@pytest.mark.asyncio
async def test_info(redisearch):
	client = redisearch('shakespeare')
	client.redis.execute_command.return_value = [
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
	client.redis.execute_command.assert_called_once_with('FT.INFO', 'shakespeare')
