from unittest import mock

import pytest  # type: ignore

from redicalsearch import GeoFilter, Highlight, Languages, NumericFilter, SearchFlags, Summarize


@pytest.mark.asyncio
@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		# Generic flags
		(
			('foobar',),
			dict(flags=SearchFlags.NO_CONTENT),
			['FT.SEARCH', 'shakespeare', 'foobar', 'NOCONTENT', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(flags=SearchFlags.VERBATIM),
			['FT.SEARCH', 'shakespeare', 'foobar', 'VERBATIM', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(flags=SearchFlags.NO_STOPWORDS),
			['FT.SEARCH', 'shakespeare', 'foobar', 'NOSTOPWORDS', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(flags=SearchFlags.WITH_SCORES),
			['FT.SEARCH', 'shakespeare', 'foobar', 'WITHSCORES', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(flags=SearchFlags.WITH_PAYLOADS),
			['FT.SEARCH', 'shakespeare', 'foobar', 'WITHPAYLOADS', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(flags=SearchFlags.WITH_SORT_KEYS),
			['FT.SEARCH', 'shakespeare', 'foobar', 'WITHSORTKEYS', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(
				flags=(
					SearchFlags.WITH_SORT_KEYS | SearchFlags.WITH_PAYLOADS
					| SearchFlags.WITH_SCORES | SearchFlags.NO_STOPWORDS  # noqa:W503
					| SearchFlags.VERBATIM | SearchFlags.NO_CONTENT  # noqa:W503
				)
			),
			[
				'FT.SEARCH', 'shakespeare', 'foobar', 'NOCONTENT', 'VERBATIM', 'NOSTOPWORDS', 'WITHSCORES',
				'WITHPAYLOADS', 'WITHSORTKEYS', 'LIMIT', 0, 10,
			],
		),
		# FILTER
		(
			('foobar',),
			dict(numeric_filter=[NumericFilter(field='myfield', minimum=5, maximum=10)]),
			['FT.SEARCH', 'shakespeare', 'foobar', 'FILTER', 'myfield', 5.0, 10.0, 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(numeric_filter=[
				NumericFilter(
					field='myfield1', maximum=10, flags=NumericFilter.Flags.EXCLUSIVE_MAX
				),
				NumericFilter(
					field='myfield2', minimum=5, flags=NumericFilter.Flags.EXCLUSIVE_MIN
				),
			]),
			[
				'FT.SEARCH', 'shakespeare', 'foobar',
				'FILTER', 'myfield1', '-inf', '(10.0',
				'FILTER', 'myfield2', '(5.0', '+inf', 'LIMIT', 0, 10
			]
		),
		# GEOFILTER
		(
			('foobar',),
			dict(geo_filter=GeoFilter(
				field='mygeofield', longitude=111.11, latitude=-96.7, radius=50,
				units=GeoFilter.Units.METERS
			)),
			[
				'FT.SEARCH', 'shakespeare', 'foobar', 'GEOFILTER', 'mygeofield',
				111.11, -96.7, 50.0, 'm', 'LIMIT', 0, 10
			],
		),
		# INKEYS
		(
			('foobar',),
			dict(in_keys=['field1', 'field2', 'field3']),
			['FT.SEARCH', 'shakespeare', 'foobar', 'INKEYS', 3, 'field1', 'field2', 'field3', 'LIMIT', 0, 10],
		),
		# INFIELDS
		(
			('foobar',),
			dict(in_fields=['field1', 'field2']),
			['FT.SEARCH', 'shakespeare', 'foobar', 'INFIELDS', 2, 'field1', 'field2', 'LIMIT', 0, 10],
		),
		# RETURN
		(
			('foobar',),
			dict(return_fields=['field1', 'field2', 'field3']),
			['FT.SEARCH', 'shakespeare', 'foobar', 'RETURN', 3, 'field1', 'field2', 'field3', 'LIMIT', 0, 10],
		),
		# SUMMARIZE
		(
			('foobar',),
			dict(summarize=Summarize()),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(summarize=Summarize(field_names=['myfield1', 'myfield2', 'myfield3'])),
			[
				'FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'FIELDS', 3, 'myfield1', 'myfield2', 'myfield3',
				'LIMIT', 0, 10
			],
		),
		(
			('foobar',),
			dict(summarize=Summarize(fragment_total=5)),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'FRAGS', 5, 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(summarize=Summarize(fragment_length=50)),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'LEN', 50, 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(summarize=Summarize(separator='|')),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'SEPARATOR', "'|'", 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(summarize=Summarize(
				field_names=['myfield1', 'myfield2'], separator=':)', fragment_total=2, fragment_length=2
			)),
			[
				'FT.SEARCH', 'shakespeare', 'foobar', 'SUMMARIZE', 'FIELDS', 2, 'myfield1', 'myfield2',
				'FRAGS', 2, 'LEN', 2, 'SEPARATOR', "':)'", 'LIMIT', 0, 10
			],
		),
		# HIGHLIGHT
		(
			('foobar',),
			dict(highlight=Highlight()),
			['FT.SEARCH', 'shakespeare', 'foobar', 'HIGHLIGHT', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(highlight=Highlight(field_names=['myfield1', 'myfield2', 'myfield3'])),
			[
				'FT.SEARCH', 'shakespeare', 'foobar', 'HIGHLIGHT', 'FIELDS', 3, 'myfield1', 'myfield2', 'myfield3',
				'LIMIT', 0, 10
			],
		),
		(
			('foobar',),
			dict(highlight=Highlight(open_tag='<i>', close_tag='</i>')),
			['FT.SEARCH', 'shakespeare', 'foobar', 'HIGHLIGHT', 'TAGS', '<i>', '</i>', 'LIMIT', 0, 10],
		),
		(
			('foobar',),
			dict(
				highlight=Highlight(field_names=['myfield1', 'myfield2'], open_tag='<i>', close_tag='</i>')
			),
			[
				'FT.SEARCH', 'shakespeare', 'foobar',
				'HIGHLIGHT', 'FIELDS', 2, 'myfield1', 'myfield2', 'TAGS', '<i>', '</i>', 'LIMIT', 0, 10
			],
		),
		# SLOP
		(
			('foobar',),
			dict(slop=5),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SLOP', 5, 'LIMIT', 0, 10],
		),
		# SLOP | INORDER
		(
			('foobar',),
			dict(flags=SearchFlags.IN_ORDER, slop=4),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SLOP', 4, 'INORDER', 'LIMIT', 0, 10],
		),
		# LANGUAGE
		(
			('foobar',),
			dict(language=Languages.DUTCH),
			['FT.SEARCH', 'shakespeare', 'foobar', 'LANGUAGE', 'dutch', 'LIMIT', 0, 10],
		),
		# EXPANDER
		(
			('foobar',),
			dict(expander='my_expander'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'EXPANDER', 'my_expander', 'LIMIT', 0, 10],
		),
		# SCORER
		(
			('foobar',),
			dict(scorer='my_scorer'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SCORER', 'my_scorer', 'LIMIT', 0, 10],
		),
		# PAYLOAD
		(
			('foobar',),
			dict(payload='asdf'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'PAYLOAD', 'asdf', 'LIMIT', 0, 10],
		),
		# SORTBY
		(
			('foobar',),
			dict(sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SORTBY', 'myfield', 'LIMIT', 0, 10],
		),
		# SORTBY | ASC
		(
			('foobar',),
			dict(flags=SearchFlags.ASC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SORTBY', 'myfield', 'ASC', 'LIMIT', 0, 10],
		),
		# SORTBY | DESC
		(
			('foobar',),
			dict(flags=SearchFlags.DESC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SORTBY', 'myfield', 'DESC', 'LIMIT', 0, 10],
		),
		# SORTBY | ASC prevails over DESC
		(
			('foobar',),
			dict(flags=SearchFlags.DESC | SearchFlags.ASC, sort_by='myfield'),
			['FT.SEARCH', 'shakespeare', 'foobar', 'SORTBY', 'myfield', 'ASC', 'LIMIT', 0, 10],
		),
		# LIMIT
		(
			('foobar',),
			dict(limit=50, offset=20),
			['FT.SEARCH', 'shakespeare', 'foobar', 'LIMIT', 20, 50],
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
@mock.patch('redicalsearch.mixin._convert_search_result')
async def test_search(__convert_search_result, args, kwargs, expected, mocked_redicalsearch):
	mocked_redicalsearch.ft.search('shakespeare', *args, **kwargs)
	mocked_redicalsearch.resource.execute.assert_called_once_with(*expected, transform=__convert_search_result())
