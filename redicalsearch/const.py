from enum import unique, Enum


@unique
class CommandCreateParameters(str, Enum):
	FILTER = 'FILTER'
	LANGUAGE = 'LANGUAGE'
	LANGUAGE_FIELD = 'LANGUAGE_FIELD'
	MAXTEXTFIELDS = 'MAXTEXTFIELDS'
	NOFIELDS = 'NOFIELDS'
	NOFREQS = 'NOFREQS'
	NOHL = 'NOHL'
	NOOFFSETS = 'NOOFFSETS'
	ON = 'ON'
	PAYLOAD_FIELD = 'PAYLOAD_FIELD'
	PREFIX = 'PREFIX'
	SCHEMA = 'SCHEMA'
	SCORE = 'SCORE'
	SCORE_FIELD = 'SCORE_FIELD'
	SKIPINITIALSCAN = 'SKIPINITIALSCAN'
	STOPWORDS = 'STOPWORDS'
	TEMPORARY = 'TEMPORARY'

	def __str__(self) -> str:
		return str(self.value)


@unique
class CommandSearchParameters(str, Enum):
	ASC = 'ASC'
	DESC = 'DESC'
	EXPANDER = 'EXPANDER'
	FIELDS = 'FIELDS'
	FILTER = 'FILTER'
	FRAGS = 'FRAGS'
	GEOFILTER = 'GEOFILTER'
	HIGHLIGHT = 'HIGHLIGHT'
	INFIELDS = 'INFIELDS'
	INKEYS = 'INKEYS'
	INORDER = 'INORDER'
	LANGUAGE = 'LANGUAGE'
	LEN = 'LEN'
	LIMIT = 'LIMIT'
	NOCONTENT = 'NOCONTENT'
	NOSTOPWORDS = 'NOSTOPWORDS'
	PAYLOAD = 'PAYLOAD'
	RETURN = 'RETURN'
	SCORER = 'SCORER'
	SEPARATOR = 'SEPARATOR'
	SLOP = 'SLOP'
	SORTBY = 'SORTBY'
	SUMMARIZE = 'SUMMARIZE'
	TAGS = 'TAGS'
	WITHPAYLOADS = 'WITHPAYLOADS'
	WITHSCORES = 'WITHSCORES'
	WITHSORTKEYS = 'WITHSORTKEYS'
	VERBATIM = 'VERBATIM'

	def __str__(self) -> str:
		return str(self.value)


@unique
class ErrorResponses(str, Enum):
	INDEX_ALREADY_EXISTS = 'index already exists'
	UNKNOWN_INDEX = 'unknown index name'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FieldParameters(str, Enum):
	NOINDEX = 'NOINDEX'
	NOSTEM = 'NOSTEM'
	PHONETIC = 'PHONETIC'
	SEPARATOR = 'SEPARATOR'
	SORTABLE = 'SORTABLE'
	WEIGHT = 'WEIGHT'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FieldTypes(str, Enum):
	GEO = 'GEO'
	NUMERIC = 'NUMERIC'
	TAG = 'TAG'
	TEXT = 'TEXT'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FullTextCommands(str, Enum):
	ADD = 'FT.ADD'
	CREATE = 'FT.CREATE'
	GET = 'FT.GET'
	INFO = 'FT.INFO'
	SEARCH = 'FT.SEARCH'

	def __str__(self) -> str:
		return str(self.value)
