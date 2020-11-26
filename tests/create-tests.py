import pytest  # type: ignore

from redicalsearch import CreateFlags, IndexOptions, Languages, Schema, TextField, SchemaTextField
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
def test_create_from_method_arguments(args, kwargs, expected, mocked_redicalsearch):
	mocked_redicalsearch.ft.create(*args, **kwargs)
	mocked_redicalsearch.resource.execute.assert_called_once_with(*expected, error_func=_check_index_exists_error)


def test_too_low_score(mocked_redicalsearch):
	with pytest.raises(ValueError, match='score must be between 0.0 and 1.0, got -1.0'):
		mocked_redicalsearch.ft.create('myindex', TextField('myfield'), score=-1)


def test_too_high_score(mocked_redicalsearch):
	with pytest.raises(ValueError, match='score must be between 0.0 and 1.0, got 2.0'):
		mocked_redicalsearch.ft.create('myindex', TextField('myfield'), score=2)


class SchemaNoOptions(Schema):
	myfield = SchemaTextField()


class Prefixes(IndexOptions):
	prefixes = ('doc:', 'aprefix:')


class SchemaPrefix(SchemaNoOptions):
	Options = Prefixes


class Filter(IndexOptions):
	filter = '@indexName=="myindex"'


class SchemaFilter(SchemaNoOptions):
	Options = Filter


class Language(IndexOptions):
	language = Languages.CHINESE


class SchemaLanguage(SchemaNoOptions):
	Options = Language


class LanguageField(IndexOptions):
	language_field = 'mylanguagefield'


class SchemaLanguageField(SchemaNoOptions):
	Options = LanguageField


class PayloadField(IndexOptions):
	payload_field = 'mypayloadfield'


class SchemaPayloadField(SchemaNoOptions):
	Options = PayloadField


class Score(IndexOptions):
	score = 0.5


class SchemaScore(SchemaNoOptions):
	Options = Score


class ScoreField(IndexOptions):
	score_field = 'myscorefield'


class SchemaScoreField(SchemaNoOptions):
	Options = ScoreField


class Stopwords(IndexOptions):
	stopwords = ['one', 'two', 'three']


class SchemaStopwords(SchemaNoOptions):
	Options = Stopwords


class Temporary(IndexOptions):
	temporary = 600


class SchemaTemporary(SchemaNoOptions):
	Options = Temporary


class Flags(IndexOptions):
	flags = (
		CreateFlags.SKIP_INITIAL_SCAN | CreateFlags.NO_OFFSETS | CreateFlags.NO_HIGHLIGHTS
		| CreateFlags.NO_FREQUENCIES | CreateFlags.NO_FIELDS | CreateFlags.MAX_TEXT_FIELDS  # noqa: W503
	)


class SchemaFlags(SchemaNoOptions):
	Options = Flags


@pytest.mark.parametrize(
	'args,expected',
	[
		(
			('myindex', SchemaNoOptions),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaPrefix),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'PREFIX', 2, 'doc:', 'aprefix:', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaFilter),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'FILTER', '@indexName=="myindex"', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaLanguage),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'LANGUAGE', 'chinese', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaLanguageField),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'LANGUAGE_FIELD', 'mylanguagefield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaPayloadField),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'PAYLOAD_FIELD', 'mypayloadfield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaScore),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCORE', '0.5', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaScoreField),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'SCORE_FIELD', 'myscorefield', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaStopwords),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'STOPWORDS', 3, 'one', 'two', 'three', 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaTemporary),
			['FT.CREATE', 'myindex', 'ON', 'HASH', 'TEMPORARY', 600, 'SCHEMA', 'myfield', 'TEXT'],
		),
		(
			('myindex', SchemaFlags),
			[
				'FT.CREATE', 'myindex', 'ON', 'HASH',
				'MAXTEXTFIELDS', 'NOFIELDS', 'NOFREQS', 'NOHL', 'NOOFFSETS', 'SKIPINITIALSCAN',
				'SCHEMA', 'myfield', 'TEXT'
			],
		),
	],
	ids=[
		'no config',
		'prefixes',
		'filter',
		'language',
		'language_field',
		'payload_field',
		'score',
		'score_field',
		'stopwords',
		'temporary',
		'flag - all',
	]
)
def test_create_from_schema_model(args, expected, mocked_redicalsearch):
	mocked_redicalsearch.ft.create(*args)
	mocked_redicalsearch.resource.execute.assert_called_once_with(*expected, error_func=_check_index_exists_error)
