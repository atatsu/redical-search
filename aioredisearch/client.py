from __future__ import annotations

import logging
from enum import auto, unique, Enum, Flag
from typing import (
	Any,
	ClassVar,
	Dict,
	List,
	Optional,
	Sequence,
	Tuple,
	Type,
	TypeVar,
	Union,
	TYPE_CHECKING,
)

from aredis import ResponseError  # type: ignore
from pydantic import BaseModel

from .const import (
	CommandAddParameters,
	CommandCreateParameters,
	CommandSearchParameters,
	ErrorResponses,
	FullTextCommands,
)
from .exception import DocumentExists, IndexExists, UnknownIndex
from .model import IndexInfo, SearchResult

if TYPE_CHECKING:
	from aredis import StrictRedis  # type: ignore
	from .field import Field as BaseField
	Field = TypeVar('Field', bound=BaseField)


__all__: List[str] = [
	'CreateFlags',
	'GeoFilter',
	'GeoFilterUnits',
	'Highlight',
	'Languages',
	'NumericFilter',
	'NumericFilterFlags',
	'ReplaceOptions',
	'RediSearch',
	'SearchFlags',
	'Summarize',
]

LOG: logging.Logger = logging.getLogger(__name__)


class CreateFlags(Flag):
	MAX_TEXT_FIELDS = auto()
	"""
	If set will force *RediSearch* to encode indexes as if there were more than 32 text fields,
	which allows for adding additional fields (beyond 32) using `RediSearch.alter_schema_add()`.
	For efficiency *RediSearch* encodes indexes differently if they are created with less than 32
	text fields.
	"""
	NO_FIELDS = auto()
	"""
	If set no field bits will be stored for each term. Saves memory but does not allow filtering
	by specific fields.
	"""
	NO_FREQUENCIES = auto()
	"""
	If set term frequencies will not be stored on the index. This saves memory but does not allow
	sorting based on the frequencies of a given term within documents.
	"""
	NO_HIGHLIGHTS = auto()
	"""
	If set highlighting support will be disabled which conserves storage space and memory. No
	corresponding byte offsets will be stored for term positions.

	Note: Implied by `CreateFlags.NO_OFFSETS`.
	"""
	NO_OFFSETS = auto()
	"""
	If set no term offsets will be stored for documents.  Saves memory but does not allow exact
	searches or highlighting.

	Note: Implies `CreateFlags.NO_HIGHLIGHTS`.
	"""


@unique
class Languages(Enum):
	ARABIC: str = 'arabic'
	CHINESE: str = 'chinese'
	DANISH: str = 'danish'
	DUTCH: str = 'dutch'
	ENGLISH: str = 'english'
	FINNISH: str = 'finnish'
	FRENCH: str = 'french'
	GERMAN: str = 'german'
	HUNGARIAN: str = 'hungarian'
	ITALIAN: str = 'italian'
	NORWEGIAN: str = 'norwegian'
	PORTUGUESE: str = 'portuguese'
	ROMANIAN: str = 'romanian'
	RUSSIAN: str = 'russian'
	SPANISH: str = 'spanish'
	SWEDISH: str = 'swedish'
	TAMIL: str = 'tamil'
	TURKISH: str = 'turkish'

	def __str__(self) -> str:
		return str(self.value)


class ReplaceOptions(Flag):
	DEFAULT = auto()
	PARTIAL = auto()
	NO_CREATE = auto()


class SearchFlags(Flag):
	ASC = auto()
	DESC = auto()
	EXPLAIN_SCORE = auto()
	IN_ORDER = auto()
	NO_CONTENT = auto()
	VERBATIM = auto()
	NO_STOPWORDS = auto()
	WITH_SCORES = auto()
	WITH_PAYLOADS = auto()
	WITH_SORT_KEYS = auto()


class GeoFilterUnits(Enum):
	FEET: str = 'ft'
	KILOMETERS: str = 'km'
	METERS: str = 'm'
	MILES: str = 'mi'

	def __str__(self) -> str:
		return str(self.value)


class GeoFilter(BaseModel):
	Units: ClassVar[Type[GeoFilterUnits]] = GeoFilterUnits

	field: str
	latitude: float
	longitude: float
	radius: float
	units: GeoFilterUnits


class Highlight(BaseModel):
	"""
	Highlighting will highlight the found term (and its variants) with a user-defined tag.
	This may be used to display the matched text in a different typeface using a markup
	language, or to otherwise make the text appear differently.
	"""
	field_names: Optional[Sequence[str]]
	"""
	Each field supplied is highlighted. If not specified then *all* fields are highlighted.
	"""
	open_tag: Optional[str]
	"""
	The opening tag to prepend to each term match.
	"""
	close_tag: Optional[str]
	"""
	The closing tag to append to each term match.
	"""


class NumericFilterFlags(Flag):
	EXCLUSIVE_MAX = auto()
	EXCLUSIVE_MIN = auto()


class NumericFilter(BaseModel):
	Flags: ClassVar[Type[NumericFilterFlags]] = NumericFilterFlags

	field: str
	maximum: Optional[float]
	minimum: Optional[float]
	flags: Optional[NumericFilterFlags]


class Summarize(BaseModel):
	"""
	Summarization will fragment the text into smaller sized snippets. Each snippet will
	contain the found term(s) and some additional surrounding context.
	"""
	field_names: Optional[Sequence[str]]
	"""
	Each field supplied is summarized. If not specified then *all* fields are summarized.
	"""
	fragment_total: Optional[int]
	"""
	Dictates how many fragments should be returned. If not specified the default value is `3`.
	"""
	fragment_length: Optional[int]
	"""
	The number of context words each fragment should contain. Context words surround
	the found term. A higher value will return a larger block of text. If not specified
	the default value is `20`.
	"""
	separator: Optional[str]
	"""
	The string used to divide between individual summary snippets. The default is `...`
	which is common among search engines.
	"""


class RediSearch:
	"""
	"""
	_index_name: str
	_redis: 'StrictRedis'

	@property
	def redis(self) -> 'StrictRedis':
		"""
		A read-only property for accessing the redis client in use by this client.
		"""
		return self._redis

	def __init__(self, index_name: str, /, *, redis: 'StrictRedis') -> None:
		self._index_name = index_name
		self._redis = redis

	async def add_document(
		self,
		doc_id: str,
		/,
		*fields: Tuple[str, Any],
		language: Optional[Languages] = None,
		no_save: bool = False,
		payload: Optional[str] = None,
		replace: Optional[ReplaceOptions] = None,
		replace_condition: Optional[str] = None,
		score: Union[float, int] = 1.0,
	) -> None:
		"""
		Add a document to the index.

		Args:
			doc_id: The document's id that will be returned from searches.
			fields: A sequence of field/value pairs to be indexed. Each field will be scored based
				on the index spec given in `~RediSearch.create_index()`. Passing fields that are not
				in the index spec will cause them to be stored as part of the document, or ignored if
				`no_save` is set.
			language: If supplied a stemmer for the chosen language is used during indexing.
				The following languages are supported:
					* `Languages.ARABIC`
					* `Languages.CHINESE`
					* `Languages.DANISH`
					* `Languages.DUTCH`
					* `Languages.ENGLISH`
					* `Languages.FINNISH`
					* `Languages.FRENCH`
					* `Languages.GERMAN`
					* `Languages.HUNGARIAN`
					* `Languages.ITALIAN`
					* `Languages.NORWEGIAN`
					* `Languages.PORTUGUESE`
					* `Languages.ROMANIAN`
					* `Languages.RUSSIAN`
					* `Languages.SPANISH`
					* `Languages.SWEDISH`
					* `Languages.TAMIL`
					* `Languages.TURKISH`

				Note:
					If indexing a Chinese language document the language **must** be set to
					`Languages.CHINESE` in order for the Chinese characters to be tokenized properly.
			no_save: If set the document will not be saved in the index but only indexed.
			payload: Optionally provide a binary safe payload string that can be evaluated at query
				time by a custom scoring function.
			replace: If set an UPSERT-style insertion is performed.

				If `ReplaceOptions.PARTIAL` is used not all fields for reindexing need to be
				specified. Fields *not* supplied will be loaded from the current version of the
				document. In addition, if only non-indexable `fields`, `score`, or `payload`
				are set, a full re-indexing of the document is not performed (and is a lot faster).

				If `ReplaceOptions.NO_CREATE` is used the document is only updated and reindexed if
				it already exists. If the document does not exist an error will be raised.
			replace_condition: Update the document only if a boolean expression applies to the
				document **before the update**.

				The expression is evaluated atomically before the update, ensuring that the update
				happens only if it is true.

				Note:
					Applicable only if `replace` options are used.

				Example:
					"@timestamp < 23323234234"
			score: The document's rank based on the user's ranking.

				Note:
					This must be between 0.0 and 1.0.
		"""
		if not fields:
			raise ValueError('Field/value pairs must be supplied')

		command: List[Any] = [str(FullTextCommands.ADD), self._index_name, doc_id, str(score)]
		if no_save:
			command.append(str(CommandAddParameters.NOSAVE))
		if isinstance(replace, ReplaceOptions):
			if replace == ReplaceOptions.DEFAULT:
				command.append(str(CommandAddParameters.REPLACE))
			elif replace == ReplaceOptions.PARTIAL:
				command.extend([str(CommandAddParameters.REPLACE), str(CommandAddParameters.PARTIAL)])
			elif replace == ReplaceOptions.NO_CREATE:
				command.extend([str(CommandAddParameters.REPLACE), str(CommandAddParameters.NOCREATE)])
			elif ReplaceOptions.PARTIAL in replace and ReplaceOptions.NO_CREATE in replace:
				command.extend([
					str(CommandAddParameters.REPLACE),
					str(CommandAddParameters.PARTIAL),
					str(CommandAddParameters.NOCREATE)
				])
		if isinstance(language, Languages):
			command.extend([str(CommandAddParameters.LANGUAGE), str(language)])
		if payload is not None:
			command.extend([str(CommandAddParameters.PAYLOAD), str(payload)])
		if replace_condition is not None:
			command.extend([str(CommandAddParameters.IF), repr(str(replace_condition))])
		command.append(str(CommandAddParameters.FIELDS))
		field: str
		value: Any
		for field, value in fields:
			value = str(value)
			if ' ' in value:
				value = repr(value)
			command.extend([field, value])
		LOG.debug(f'executing command: {" ".join(command)}')
		try:
			await self._redis.execute_command(*command)
		except ResponseError as ex:
			if str(ex).lower() == str(ErrorResponses.DOCUMENT_ALREADY_EXISTS):
				raise DocumentExists(doc_id)
			raise

	async def create_index(
		self,
		*fields: 'Field',
		flags: Optional[CreateFlags] = None,
		stopwords: Optional[Sequence[str]] = None,
		temporary: Union[float, int] = 0,
	) -> None:
		"""
		Create an index with the given spec. The index name will be used in all the
		key names so keep it short!

		Args:
			fields: A sequence of fields for the index.
			flags: The following flags are accepted:
				* `CreateFlags.MAX_TEXT_FIELDS`
				* `CreateFlags.NO_FIELDS`
				* `CreateFlags.NO_FREQUENCIES`
				* `CreateFlags.NO_HIGHLIGHTS`
				* `CreateFlags.NO_OFFSETS`
			stopwords: If supplied the index will be set with a custom stopword list
				to be ignored during indexing and search time.

				If not supplied the default stopwords will be used.

				If an empty sequence the created index will not have stopwords.
			temporary: If non-zero the created index will expire after the specified
				number of seconds of inactivity. The internal idle timer is reset whenever
				the index is searched or added to. Because such indexes are lightweight
				thousands of them can be created without negative performance implications.
		"""
		command: List[Any] = [str(FullTextCommands.CREATE), self._index_name]
		if flags is not None and CreateFlags.MAX_TEXT_FIELDS in flags:
				command.append(str(CommandCreateParameters.MAXTEXTFIELDS))
		if temporary > 0:
			command.extend([str(CommandCreateParameters.TEMPORARY), str(temporary)])
		if flags is not None:
			if CreateFlags.NO_OFFSETS in flags:
				command.append(str(CommandCreateParameters.NOOFFSETS))
			if CreateFlags.NO_HIGHLIGHTS in flags:
				command.append(str(CommandCreateParameters.NOHL))
			if CreateFlags.NO_FIELDS in flags:
				command.append(str(CommandCreateParameters.NOFIELDS))
			if CreateFlags.NO_FREQUENCIES in flags:
				command.append(str(CommandCreateParameters.NOFREQS))
		if stopwords is not None:
			num: str = str(len(stopwords))
			command.extend([str(CommandCreateParameters.STOPWORDS), num, *stopwords])
		command.append(str(CommandCreateParameters.SCHEMA))
		f: 'BaseField'
		x: Any
		command.extend([x for f in fields for x in f])
		LOG.debug(f'executing command: {" ".join(command)}')
		try:
			await self._redis.execute_command(*command)
		except ResponseError as ex:
			if str(ex).lower() == str(ErrorResponses.INDEX_ALREADY_EXISTS):
				raise IndexExists(self._index_name)
			raise

	async def info(
		self
	) -> IndexInfo:
		"""
		Returns information and statistics on the index. Returned values include:
			* number of documents
			* number of distinct terms
			* average bytes per record
			* size and capacity of the index buffers
		"""
		command: List[str] = [str(FullTextCommands.INFO), self._index_name]
		LOG.debug(f'executing command: {" ".join(command)}')
		try:
			res: List[Any] = await self._redis.execute_command(*command)
		except ResponseError as ex:
			if str(ex).lower() == str(ErrorResponses.UNKNOWN_INDEX):
				raise UnknownIndex(self._index_name)
			raise
		x: int
		mapped: Dict[str, Any] = {res[x]: res[x + 1] for x in range(0, len(res), 2)}
		return IndexInfo(**mapped)

	async def search(
		self,
		query: str,
		/,
		*,
		expander: Optional[str] = None,
		flags: Optional[SearchFlags] = None,
		geo_filter: Optional[GeoFilter] = None,
		highlight: Optional[Highlight] = None,
		in_keys: Optional[Sequence[str]] = None,
		in_fields: Optional[Any] = None,
		language: Optional[Languages] = None,
		limit: Optional[Tuple[int, int]] = None,
		numeric_filter: Optional[Sequence[NumericFilter]] = None,
		payload: Optional[str] = None,
		return_fields: Optional[Sequence[str]] = None,
		scorer: Optional[str] = None,
		slop: Optional[int] = None,
		sort_by: Optional[str] = None,
		summarize: Optional[Summarize] = None,
	) -> SearchResult:
		"""
		Searches the index with a textual query.

		Args:
			query: The text query to search.
			expander: Use a custom query expander instead of the stemmer.

				Note: See https://oss.redislabs.com/redisearch/Extensions/
			flags: `SearchFlags`
				* `SearchFlags.EXPLAIN_SCORE`: Return a textual description of how the scores
					were calculated. Only relevant in conjunction with `SearchFlags.WITH_SCORES`
					or `scorer`.
				* `SearchFlags.IN_ORDER`: Used in conjunction with `slop`, will cause the query
					terms to appear in the same order in the document as in the query,
					regardless of the offsets between them.
				* `SearchFlags.NO_CONTENT`: Only return the document ids and not the content.
				* `SearchFlags.NO_STOPWORDS`: Do not filter stopwords from the query.
				* `SearchFlags.VERBATIM`: Try not to use stemming for query expansion. Instead
					search the query terms verbatim.
				* `SearchFlags.WITH_PAYLOADS`: Retrieve optional document payloads (see
					`RediSearch.add_document`). The payloads follow the document id, and if
					`SearchFlags.WITH_SCORES` was set, follow the scores.
				* `SearchFlags.WITH_SCORES`: Return the relative internal score of each document.
					This can be used to merge results from multiple instances.
				* `SearchFlags.WITH_SORT_KEYS`: Only relevant in conjunction with `sort_by`.
					Returns the value of the sorting key, right after the id and score and/or
					payload if requested. This is usually not needed by users and exists for
					distributed search coordination purposes.
			geo_filter: Filter the results to a given radius from the supplied longitude and latitude.
			highlight: Format occurrences of matched text.

				Note: See https://oss.redislabs.com/redisearch/Highlight/
			in_keys: Limit the result to a given set of keys. Non-existent keys are ignored -
				unless all the keys are non-existent.
			in_fields: Filter the results to those matching the supplied `query` **only** in specific
				fields of the document.
			language: If supplied a stemmer for the chosen language is used during search for
				query expansion. Defaults to English. The following languages are supported:
					* `Languages.ARABIC`
					* `Languages.CHINESE`
					* `Languages.DANISH`
					* `Languages.DUTCH`
					* `Languages.ENGLISH`
					* `Languages.FINNISH`
					* `Languages.FRENCH`
					* `Languages.GERMAN`
					* `Languages.HUNGARIAN`
					* `Languages.ITALIAN`
					* `Languages.NORWEGIAN`
					* `Languages.PORTUGUESE`
					* `Languages.ROMANIAN`
					* `Languages.RUSSIAN`
					* `Languages.SPANISH`
					* `Languages.SWEDISH`
					* `Languages.TAMIL`
					* `Languages.TURKISH`

				Note:
					If querying documents in Chinese, this should be set to `Languages.CHINESE` in
					order to properly tokenize the query terms.
			limit: Limit the results to the supplied offset and count in the form of `(offset, count)`.

				Note:
					You can use `(0, 0)` to count the number of documents in the result set without
					actually returning them.
			numeric_filter: Limit results to those having numeric values ranging between the supplied
				minimum and maximum values. If no minimum is supplied `-inf` will be used. If no
				maximum is supplied `+inf` will be used.

				Note: Only applies to numeric fields.
			payload: Add an arbitrary binary safe payload that will be exposed to custom scoring
				functions.

				Note: See https://oss.redislabs.com/redisearch/Extensions/
			return_fields: Limits which fields are returned from the document.
			scorer: Use a custom scoring function.

				Note: See https://oss.redislabs.com/redisearch/Extensions/
			slop: Allow a maximum of *N* intervening number of unmatched offsets between phrase
				terms (the slop for exact phrases is 0).
			sort_by: If used and the supplied field was marked as sortable during index creation
				the results are ordered by the value of this field. Can also use the following
				`flags` to affect sort order:
					* `SearchFlags.ASC`
					* `SearchFlags.DESC`

				Note: This applies to numeric, tag, and text fields.
			summarize: Only return the sections of the field which contain the matched text.

				Note: See https://oss.redislabs.com/redisearch/Highlight/
		"""
		# kwargs are handled in the order they appear in the `FT.SEARCH` docs:
		# https://oss.redislabs.com/redisearch/Commands/#ftsearch
		command: List[Any] = [str(FullTextCommands.SEARCH), self._index_name, repr(query)]
		if flags is not None:
			if SearchFlags.NO_CONTENT in flags:
				command.append(str(CommandSearchParameters.NOCONTENT))
			if SearchFlags.VERBATIM in flags:
				command.append(str(CommandSearchParameters.VERBATIM))
			if SearchFlags.NO_STOPWORDS in flags:
				command.append(str(CommandSearchParameters.NOSTOPWORDS))
			if SearchFlags.WITH_SCORES in flags:
				command.append(str(CommandSearchParameters.WITHSCORES))
			if SearchFlags.WITH_PAYLOADS in flags:
				command.append(str(CommandSearchParameters.WITHPAYLOADS))
			if SearchFlags.WITH_SORT_KEYS in flags:
				command.append(str(CommandSearchParameters.WITHSORTKEYS))

		if numeric_filter is not None:
			filter_: NumericFilter
			for filter_ in numeric_filter:
				flags_: Optional[NumericFilterFlags] = filter_.flags
				args: List[Any] = [str(CommandSearchParameters.FILTER), filter_.field]
				min_: Optional[Union[float, str]] = filter_.minimum
				if min_ is not None and flags_ is not None and NumericFilterFlags.EXCLUSIVE_MIN in flags_:
					min_ = f'({min_}'
				args.append(min_ if min_ is not None else '-inf')
				max_: Optional[Union[float, str]] = filter_.maximum
				if max_ is not None and flags_ is not None and NumericFilterFlags.EXCLUSIVE_MAX in flags_:
					max_ = f'({max_}'
				args.append(max_ if max_ is not None else '+inf')
				command.extend(args)

		if geo_filter is not None:
			# FIXME: Ensure `GeoFilter`
			command.extend([
				str(CommandSearchParameters.GEOFILTER),
				geo_filter.field,
				geo_filter.longitude,
				geo_filter.latitude,
				geo_filter.radius,
				str(geo_filter.units)
			])

		if in_keys is not None:
			# FIXME: Throw error if len() < 0?
			_in_keys: Tuple[str, ...] = tuple(in_keys)
			command.extend([str(CommandSearchParameters.INKEYS), len(_in_keys), *_in_keys])

		if in_fields is not None:
			# FIXME: Throw error if len() < 0?
			_in_fields: Tuple[str, ...] = tuple(in_fields)
			command.extend([str(CommandSearchParameters.INFIELDS), len(_in_fields), *_in_fields])

		if return_fields is not None:
			_return_fields: Tuple[str, ...] = tuple(return_fields)
			command.extend([str(CommandSearchParameters.RETURN), len(_return_fields), *_return_fields])

		fields: Tuple[str, ...]

		if summarize is not None:
			command.append(str(CommandSearchParameters.SUMMARIZE))
			if summarize.field_names is not None:
				fields = tuple(summarize.field_names)
				command.extend([str(CommandSearchParameters.FIELDS), len(fields), *fields])
			if summarize.fragment_total is not None:
				command.extend([str(CommandSearchParameters.FRAGS), int(summarize.fragment_total)])
			if summarize.fragment_length is not None:
				command.extend([str(CommandSearchParameters.LEN), int(summarize.fragment_length)])
			if summarize.separator is not None:
				command.extend([str(CommandSearchParameters.SEPARATOR), repr(summarize.separator)])

		if highlight is not None:
			command.append(str(CommandSearchParameters.HIGHLIGHT))
			if highlight.field_names is not None:
				fields = tuple(highlight.field_names)
				command.extend([str(CommandSearchParameters.FIELDS), len(fields), *fields])
			# FIXME: Throw error if one is not none but the other is?
			if highlight.close_tag is not None and highlight.open_tag is not None:
				command.extend([str(CommandSearchParameters.TAGS), str(highlight.open_tag), str(highlight.close_tag)])

		if slop is not None:
			command.extend([str(CommandSearchParameters.SLOP), int(slop)])
		# Intentionally allowing INORDER through even if SLOP isn't used as the docs make it sound like
		# it is only "usually" used with SLOP, so we can use it without?
		if flags is not None and SearchFlags.IN_ORDER in flags:
			command.append(str(CommandSearchParameters.INORDER))

		if language is not None:
			command.extend([str(CommandSearchParameters.LANGUAGE), str(language)])

		if expander is not None:
			command.extend([str(CommandSearchParameters.EXPANDER), expander])

		if scorer is not None:
			command.extend([str(CommandSearchParameters.SCORER), scorer])

		if payload is not None:
			command.extend([str(CommandSearchParameters.PAYLOAD), payload])

		if sort_by is not None:
			command.extend([str(CommandSearchParameters.SORTBY), sort_by])
			if flags is not None and SearchFlags.ASC in flags:
				command.append(str(CommandSearchParameters.ASC))
			elif flags is not None and SearchFlags.DESC in flags:
				command.append(str(CommandSearchParameters.DESC))

		offset: int = 0
		limit_: int = 0
		if limit is not None:
			offset, limit_ = (int(limit[0]), int(limit[1]))
			command.extend([str(CommandSearchParameters.LIMIT), offset, limit_])

		LOG.debug(f'executing command: {" ".join(map(str, command))}')
		raw_results: List[Any] = await self._redis.execute_command(*command)
		total: int = raw_results[0]
		x: int
		y: int
		mapped: List[Dict[str, Any]] = [
			dict(
				document_id=raw_results[x],
				document={
					raw_results[x + 1][y]: raw_results[x + 1][y + 1] for y in range(0, len(raw_results[x + 1]), 2)
				}
			)
			for x in range(1, len(raw_results[1:]), 2)
		]
		return SearchResult(results=mapped, count=len(mapped), total=total, offset=offset, limit=limit_)

	CreateFlags: ClassVar[Type[CreateFlags]] = CreateFlags
	GeoFilter: ClassVar[Type[GeoFilter]] = GeoFilter
	Highlight: ClassVar[Type[Highlight]] = Highlight
	Languages: ClassVar[Type[Languages]] = Languages
	NumericFilter: ClassVar[Type[NumericFilter]] = NumericFilter
	ReplaceOptions: ClassVar[Type[ReplaceOptions]] = ReplaceOptions
	SearchFlags: ClassVar[Type[SearchFlags]] = SearchFlags
	Summarize: ClassVar[Type[Summarize]] = Summarize
