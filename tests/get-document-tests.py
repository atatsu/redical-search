import pytest  # type: ignore


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			('adocid',),
			{},
			['FT.GET', 'shakespeare', 'adocid'],
		),
	]
)
async def test_get_document(args, kwargs, expected, mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	await client.get_document(*args, **kwargs)
	client.redis.execute_command.assert_called_once_with(*expected)
