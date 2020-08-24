from enum import unique, Enum


@unique
class CommandAddParameters(Enum):
	FIELDS: str = 'FIELDS'
	IF: str = 'IF'
	LANGUAGE: str = 'LANGUAGE'
	NOCREATE: str = 'NOCREATE'
	NOSAVE: str = 'NOSAVE'
	PARTIAL: str = 'PARTIAL'
	PAYLOAD: str = 'PAYLOAD'
	REPLACE: str = 'REPLACE'

	def __str__(self) -> str:
		return str(self.value)


@unique
class CommandCreateParameters(Enum):
	MAXTEXTFIELDS: str = 'MAXTEXTFIELDS'
	NOHL: str = 'NOHL'
	NOFIELDS: str = 'NOFIELDS'
	NOFREQS: str = 'NOFREQS'
	NOOFFSETS: str = 'NOOFFSETS'
	STOPWORDS: str = 'STOPWORDS'
	SCHEMA: str = 'SCHEMA'
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
