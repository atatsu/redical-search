import pytest  # type: ignore

from aioredisearch import RediSearch


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		# Generic flags
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.NO_CONTENT),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'NOCONTENT'],
		),
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.VERBATIM),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'VERBATIM'],
		),
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.NO_STOPWORDS),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'NOSTOPWORDS'],
		),
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.WITH_SCORES),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'WITHSCORES'],
		),
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.WITH_PAYLOADS),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'WITHPAYLOADS'],
		),
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.WITH_SORT_KEYS),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'WITHSORTKEYS'],
		),
		(
			('foobar',),
			dict(
				flags=(
					RediSearch.SearchFlags.WITH_SORT_KEYS | RediSearch.SearchFlags.WITH_PAYLOADS
					| RediSearch.SearchFlags.WITH_SCORES | RediSearch.SearchFlags.NO_STOPWORDS  # noqa:W503
					| RediSearch.SearchFlags.VERBATIM | RediSearch.SearchFlags.NO_CONTENT  # noqa:W503
				)
			),
			[
				'FT.SEARCH', 'shakespeare', "'foobar'", 'NOCONTENT', 'VERBATIM', 'NOSTOPWORDS', 'WITHSCORES',
				'WITHPAYLOADS', 'WITHSORTKEYS',
			],
		),
		# FILTER
		(
			('foobar',),
			dict(numeric_filter=[RediSearch.NumericFilter(field='myfield', minimum=5, maximum=10)]),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'FILTER', 'myfield', 5.0, 10.0],
		),
		(
			('foobar',),
			dict(numeric_filter=[
				RediSearch.NumericFilter(field='myfield1', maximum=10, flags=RediSearch.NumericFilter.Flags.EXCLUSIVE_MAX),
				RediSearch.NumericFilter(field='myfield2', minimum=5, flags=RediSearch.NumericFilter.Flags.EXCLUSIVE_MIN),
			]),
			[
				'FT.SEARCH', 'shakespeare', "'foobar'",
				'FILTER', 'myfield1', '-inf', '(10.0',
				'FILTER', 'myfield2', '(5.0', '+inf'
			]
		),
		# GEOFILTER
		(
			('foobar',),
			dict(geo_filter=RediSearch.GeoFilter(
				field='mygeofield', longitude=111.11, latitude=-96.7, radius=50, units=RediSearch.GeoFilter.Units.METERS
			)),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'GEOFILTER', 'mygeofield', 111.11, -96.7, 50.0, 'm'],
		),
		# INKEYS
		(
			('foobar',),
			dict(in_keys=['field1', 'field2', 'field3']),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'INKEYS', 3, 'field1', 'field2', 'field3'],
		),
		# INFIELDS
		(
			('foobar',),
			dict(in_fields=['field1', 'field2']),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'INFIELDS', 2, 'field1', 'field2'],
		),
		# RETURN
		(
			('foobar',),
			dict(return_fields=['field1', 'field2', 'field3']),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'RETURN', 3, 'field1', 'field2', 'field3'],
		),
		# SUMMARIZE
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize()),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE'],
		),
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize(field_names=['myfield1', 'myfield2', 'myfield3'])),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE', 'FIELDS', 3, 'myfield1', 'myfield2', 'myfield3'],
		),
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize(fragment_total=5)),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE', 'FRAGS', 5],
		),
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize(fragment_length=50)),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE', 'LEN', 50],
		),
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize(separator='|')),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE', 'SEPARATOR', "'|'"],
		),
		(
			('foobar',),
			dict(summarize=RediSearch.Summarize(
				field_names=['myfield1', 'myfield2'], separator=':)', fragment_total=2, fragment_length=2
			)),
			[
				'FT.SEARCH', 'shakespeare', "'foobar'", 'SUMMARIZE', 'FIELDS', 2, 'myfield1', 'myfield2',
				'FRAGS', 2, 'LEN', 2, 'SEPARATOR', "':)'"
			],
		),
		# HIGHLIGHT
		(
			('foobar',),
			dict(highlight=RediSearch.Highlight()),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'HIGHLIGHT'],
		),
		(
			('foobar',),
			dict(highlight=RediSearch.Highlight(field_names=['myfield1', 'myfield2', 'myfield3'])),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'HIGHLIGHT', 'FIELDS', 3, 'myfield1', 'myfield2', 'myfield3'],
		),
		(
			('foobar',),
			dict(highlight=RediSearch.Highlight(open_tag='<i>', close_tag='</i>')),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'HIGHLIGHT', 'TAGS', '<i>', '</i>'],
		),
		(
			('foobar',),
			dict(
				highlight=RediSearch.Highlight(field_names=['myfield1', 'myfield2'], open_tag='<i>', close_tag='</i>')
			),
			[
				'FT.SEARCH', 'shakespeare', "'foobar'",
				'HIGHLIGHT', 'FIELDS', 2, 'myfield1', 'myfield2', 'TAGS', '<i>', '</i>'
			],
		),
		# SLOP
		(
			('foobar',),
			dict(slop=5),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SLOP', 5],
		),
		# SLOP | INORDER
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.IN_ORDER, slop=4),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SLOP', 4, 'INORDER'],
		),
		# LANGUAGE
		(
			('foobar',),
			dict(language=RediSearch.Languages.DUTCH),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'LANGUAGE', 'dutch'],
		),
		# EXPANDER
		(
			('foobar',),
			dict(expander='my_expander'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'EXPANDER', 'my_expander'],
		),
		# SCORER
		(
			('foobar',),
			dict(scorer='my_scorer'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SCORER', 'my_scorer'],
		),
		# PAYLOAD
		(
			('foobar',),
			dict(payload='asdf'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'PAYLOAD', 'asdf'],
		),
		# SORTBY
		(
			('foobar',),
			dict(sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SORTBY', 'myfield'],
		),
		# SORTBY | ASC
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.ASC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SORTBY', 'myfield', 'ASC'],
		),
		# SORTBY | DESC
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.DESC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SORTBY', 'myfield', 'DESC'],
		),
		# SORTBY | ASC prevails over DESC
		(
			('foobar',),
			dict(flags=RediSearch.SearchFlags.DESC | RediSearch.SearchFlags.ASC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'SORTBY', 'myfield', 'ASC'],
		),
		# LIMIT
		(
			('foobar',),
			dict(limit=(20, 50)),
			['FT.SEARCH', 'shakespeare', "'foobar'", 'LIMIT', 20, 50],
		),
	],
	ids=[
		'flag - NOCONTENT',
		'flag - VERBATIM',
		'flag - NOSTOPWORDS',
		'flag - WITHSCORES',
		'flag - WITHPAYLOADS',
		'flag - WITHSORTKEYS',
		'flag - all',
		'FILTER',
		'FILTER | -inf | +inf | exclusive min/max',
		'GEOFILTER',
		'INKEYS',
		'INFIELDS',
		'RETURN',
		'SUMMARIZE',
		'SUMMARIZE | FIELDS',
		'SUMMARIZE | FRAGS',
		'SUMMARIZE | LEN',
		'SUMMARIZE | SEPARATOR',
		'SUMMARIZE | FIELDS | FRAGS | LEN | SEPARATOR',
		'HIGHLIGHT',
		'HIGHTLIGHT | FIELDS',
		'HIGHLIGHT | TAGS',
		'HIGHLIGHT | FIELDS | TAGS',
		'SLOP',
		'SLOP | INORDER',
		'LANGUAGE',
		'EXPANDER',
		'SCORER',
		'PAYLOAD',
		'SORTBY',
		'SORTBY | ASC',
		'SORTBY | DESC',
		'SORTBY | ASC prevails over DESC',
		'LIMIT',
	]
)
async def test_search(args, kwargs, expected, mocked_redisearch):
	client = mocked_redisearch('shakespeare')
	await client.search(*args, **kwargs)
	client.redis.execute_command.assert_called_once_with(*expected)
