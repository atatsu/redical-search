from enum import unique, Enum


@unique
class CommandCreateParameters(Enum):
	FILTER: str = 'FILTER'
	LANGUAGE: str = 'LANGUAGE'
	LANGUAGE_FIELD: str = 'LANGUAGE_FIELD'
	MAXTEXTFIELDS: str = 'MAXTEXTFIELDS'
	NOFIELDS: str = 'NOFIELDS'
	NOFREQS: str = 'NOFREQS'
	NOHL: str = 'NOHL'
	NOOFFSETS: str = 'NOOFFSETS'
	ON: str = 'ON'
	PAYLOAD_FIELD: str = 'PAYLOAD_FIELD'
	PREFIX: str = 'PREFIX'
	SCHEMA: str = 'SCHEMA'
	SCORE: str = 'SCORE'
	SCORE_FIELD: str = 'SCORE_FIELD'
	SKIPINITIALSCAN: str = 'SKIPINITIALSCAN'
	STOPWORDS: str = 'STOPWORDS'
	TEMPORARY: str = 'TEMPORARY'

	def __str__(self) -> str:
		return str(self.value)


@unique
class CommandSearchParameters(Enum):
	ASC: str = 'ASC'
	DESC: str = 'DESC'
	EXPANDER: str = 'EXPANDER'
	FIELDS: str = 'FIELDS'
	FILTER: str = 'FILTER'
	FRAGS: str = 'FRAGS'
	GEOFILTER: str = 'GEOFILTER'
	HIGHLIGHT: str = 'HIGHLIGHT'
	INFIELDS: str = 'INFIELDS'
	INKEYS: str = 'INKEYS'
	INORDER: str = 'INORDER'
	LANGUAGE: str = 'LANGUAGE'
	LEN: str = 'LEN'
	LIMIT: str = 'LIMIT'
	NOCONTENT: str = 'NOCONTENT'
	NOSTOPWORDS: str = 'NOSTOPWORDS'
	PAYLOAD: str = 'PAYLOAD'
	RETURN: str = 'RETURN'
	SCORER: str = 'SCORER'
	SEPARATOR: str = 'SEPARATOR'
	SLOP: str = 'SLOP'
	SORTBY: str = 'SORTBY'
	SUMMARIZE: str = 'SUMMARIZE'
	TAGS: str = 'TAGS'
	WITHPAYLOADS: str = 'WITHPAYLOADS'
	WITHSCORES: str = 'WITHSCORES'
	WITHSORTKEYS: str = 'WITHSORTKEYS'
	VERBATIM: str = 'VERBATIM'

	def __str__(self) -> str:
		return str(self.value)


@unique
class ErrorResponses(Enum):
	DOCUMENT_ALREADY_EXISTS: str = 'document already exists'
	INDEX_ALREADY_EXISTS: str = 'index already exists'
	UNKNOWN_INDEX: str = 'unknown index name'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FieldParameters(Enum):
	NOINDEX: str = 'NOINDEX'
	NOSTEM: str = 'NOSTEM'
	PHONETIC: str = 'PHONETIC'
	SEPARATOR: str = 'SEPARATOR'
	SORTABLE: str = 'SORTABLE'
	WEIGHT: str = 'WEIGHT'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FieldTypes(Enum):
	GEO: str = 'GEO'
	NUMERIC: str = 'NUMERIC'
	TAG: str = 'TAG'
	TEXT: str = 'TEXT'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FullTextCommands(Enum):
	ADD: str = 'FT.ADD'
	CREATE: str = 'FT.CREATE'
	GET: str = 'FT.GET'
	INFO: str = 'FT.INFO'
	SEARCH: str = 'FT.SEARCH'

	def __str__(self) -> str:
		return str(self.value)
