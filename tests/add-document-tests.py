import pytest  # type: ignore

from aioredisearch import RediSearch


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			{},
			['FT.ADD', 'shakespeare', 'adocid', '1.0', 'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'],
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(score=5),
			['FT.ADD', 'shakespeare', 'adocid', '5', 'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'],
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(no_save=True),
			['FT.ADD', 'shakespeare', 'adocid', '1.0', 'NOSAVE', 'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234']
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.DEFAULT),
			['FT.ADD', 'shakespeare', 'adocid', '1.0', 'REPLACE', 'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234']
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.PARTIAL),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'REPLACE', 'PARTIAL',
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.NO_CREATE),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'REPLACE', 'NOCREATE',
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace=RediSearch.ReplaceOptions.NO_CREATE | RediSearch.ReplaceOptions.PARTIAL),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'REPLACE', 'PARTIAL', 'NOCREATE',
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(language=RediSearch.Languages.RUSSIAN),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'LANGUAGE', 'russian',
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(payload='asdf'),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'PAYLOAD', 'asdf',
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(replace_condition='@timestamp < 23323234234'),
			[
				'FT.ADD', 'shakespeare', 'adocid', '1.0', 'IF', "'@timestamp < 23323234234'",
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
		(
			(
				'adocid',
				*dict(foo='bar baz', bar='baz', baz=1234).items()
			),
			dict(
				language=RediSearch.Languages.SWEDISH,
				no_save=True,
				payload='asdf',
				replace=RediSearch.ReplaceOptions.NO_CREATE | RediSearch.ReplaceOptions.PARTIAL,
				replace_condition='@timestamp < 23323234234',
				score=5.5,
			),
			[
				'FT.ADD', 'shakespeare', 'adocid', '5.5', 'NOSAVE', 'REPLACE', 'PARTIAL', 'NOCREATE',
				'LANGUAGE', 'swedish', 'PAYLOAD', 'asdf', 'IF', "'@timestamp < 23323234234'",
				'FIELDS', 'foo', "'bar baz'", 'bar', 'baz', 'baz', '1234'
			]
		),
	]
)
async def test_add_document(args, kwargs, expected, redisearch):
	client = redisearch('shakespeare')
	await client.add_document(*args, **kwargs)
	client.redis.execute_command.assert_called_once_with(*expected)


@pytest.mark.asyncio
async def test_add_document_no_fields(redisearch):
	client = redisearch('shakespeare')
	with pytest.raises(ValueError, match='Field/value pairs must be supplied'):
		await client.add_document('adocid')
