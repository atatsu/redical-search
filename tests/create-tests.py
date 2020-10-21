import pytest  # type: ignore

from redicalsearch import CreateFlags, Languages, TextField
from redicalsearch.mixin import _check_index_exists_error


@pytest.mark.parametrize(
	'args,kwargs,expected',
	[
		(
			('myindex', *(TextField('myfield'),)),
			dict(),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(prefixes=['doc:', 'aprefix:']),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'PREFIX', 2, 'doc:', 'aprefix:', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(filter='@indexName=="myindex"'),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'FILTER', '@indexName=="myindex"', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(language=Languages.CHINESE),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'LANGUAGE', 'chinese', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(language_field='mylanguagefield'),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'LANGUAGE_FIELD', 'mylanguagefield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(payload_field='mypayloadfield'),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'PAYLOAD_FIELD', 'mypayloadfield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(score=0.5),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCORE', '0.5', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(score_field='myscorefield'),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCORE_FIELD', 'myscorefield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(stopwords=['one', 'two', 'three']),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'STOPWORDS', 3, 'one', 'two', 'three', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(temporary=600),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'TEMPORARY', 600, 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.MAX_TEXT_FIELDS),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'MAXTEXTFIELDS', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.NO_FIELDS),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'NOFIELDS', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.NO_FREQUENCIES),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'NOFREQS', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.NO_HIGHLIGHTS),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'NOHL', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.NO_OFFSETS),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'NOOFFSETS', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(flags=CreateFlags.SKIP_INITIAL_SCAN),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SKIPINITIALSCAN', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', *(TextField('myfield'),)),
			dict(
				flags=CreateFlags.SKIP_INITIAL_SCAN | CreateFlags.NO_OFFSETS | CreateFlags.NO_HIGHLIGHTS
				| CreateFlags.NO_FREQUENCIES | CreateFlags.NO_FIELDS | CreateFlags.MAX_TEXT_FIELDS  # noqa: W503
			),
			[
				'FT.CREATE', 'myindex', 'ON', 'HASH',
				'MAXTEXTFIELDS', 'NOFIELDS', 'NOFREQS', 'NOHL', 'NOOFFSETS', 'SKIPINITIALSCAN',
				'SCHEMA', 'myfield', 'TEXT'
			],
		),
	],
	ids=[
		'no parameters',
		'prefixes',
		'filter',
		'language',
		'language_field',
		'payload_field',
		'score',
		'score_field',
		'stopwords',
		'temporary',
		'flag - MAX_TEXT_FIELDS',
		'flag - NO_FIELDS',
		'flag - NO_FREQUENCIES',
		'flag - NO_HIGHLIGHTS',
		'flag - NO_OFFSETS',
		'flag - SKIP_INITIAL_SCAN',
		'flag - all',
	],
)
def test_create(args, kwargs, expected, mocked_redicalsearch):
	mocked_redicalsearch.ft.create(*args, **kwargs)
	mocked_redicalsearch.resource.execute.assert_called_once_with(*expected, error_func=_check_index_exists_error)


def test_too_low_score(mocked_redicalsearch):
	with pytest.raises(ValueError, match='score must be between 0.0 and 1.0, got -1.0'):
		mocked_redicalsearch.ft.create('myindex', TextField('myfield'), score=-1)


def test_too_high_score(mocked_redicalsearch):
	with pytest.raises(ValueError, match='score must be between 0.0 and 1.0, got 2.0'):
		mocked_redicalsearch.ft.create('myindex', TextField('myfield'), score=2)
