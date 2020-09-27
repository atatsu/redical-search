from __future__ import annotations

import logging
from enum import auto, unique, Enum, Flag
from typing import (
	Any,
	Awaitable,
	ClassVar,
	Dict,
	List,
	Optional,
	Sequence,
	Tuple,
	Type,
	Union,
	TYPE_CHECKING,
)

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from redical import RedicalBase, RedicalResource

from .const import (
	CommandCreateParameters,
	CommandSearchParameters,
	ErrorResponses,
	FullTextCommands,
)
from .exception import DocumentNotFoundError, IndexExistsError, ResponseError, UnknownIndexError
from .flag import CreateFlags
from .model import Document, IndexInfo, SearchResult

if TYPE_CHECKING:
	from .field import Field


__all__: List[str] = [
	'Geo',
	'GeoFilter',
	'GeoFilterUnits',
	'Highlight',
	'Languages',
	'NumericFilter',
	'NumericFilterFlags',
	'ReplaceOptions',
	'FTCommandsMixin',
	'SearchFlags',
	'Summarize',
]

LOG: logging.Logger = logging.getLogger(__name__)


@dataclass
class Geo:
	latitude: float
	longitude: float

	def __str__(self) -> str:
		return f'{self.longitude},{self.latitude}'


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


@unique
class Structures(Enum):
	HASH: str = 'HASH'

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


def _check_index_exists_error(exc: Exception) -> Exception:
	if 'index already exists' in str(exc).lower():
		return IndexExistsError(str(exc))
	return exc


class Commands(RedicalBase):
	def create(
		self,
		name: str,
		/,
		*fields: 'Field',
		on: Structures = Structures.HASH,
		prefix: Optional[Sequence[str]] = None,
		filter: Optional[str] = None,
		flags: Optional[CreateFlags] = None,
		language: Optional[Languages] = None,
		language_field: Optional[str] = None,
		payload_field: Optional[str] = None,
		score: Optional[Union[float, int]] = None,
		score_field: Optional[str] = None,
		stopwords: Optional[Sequence[str]] = None,
		temporary: Optional[int] = None,
	) -> Awaitable[bool]:
		"""
		Create an index with the given spec.

		Args:
			index: The index name to create. If it exists the old spec will be overwritten.
			*fields: A variable length list of fields for the index.
			on: Structure to use for documents in the created index.

				Note:
					Currently only supports `Structures.HASH`.
			prefix: Tells the index which keys it should index. If not supplied all keys
				will be indexed.
			filter: A filter expression with the full *RediSearch* aggregation expression
				language.
			flags: The following flags are accepted:
				* `CreateFlags.MAX_TEXT_FIELDS`
				* `CreateFlags.NO_FIELDS`
				* `CreateFlags.NO_FREQUENCIES`
				* `CreateFlags.NO_HIGHLIGHTS`
				* `CreateFlags.NO_OFFSETS`
				* `CreateFlags.SKIP_INITIAL_SCAN`
			language: If set indicates the default language for documents in the index.
				Default is `Languages.ENGLISH`

				Note:
					When adding Chinese-language documents `Languages.CHINESE` should be
					set in order for the indexer to properly tokenize the terms.
			language_field: If set indicates the document field that should be used as
				the document language.
			payload_field: If set indicates the document field that should be used as a
				binary safe payload string for the document that can be evaluated at query
				time by a custom scoring function, or retrieved by the client.
			score: If set indicates the default score for documents in the index. Default
				score is 1.0.
			score_field: If set indicates the document field that should be used as the
				document's rank based on the user's ranking. Ranking must be between 0.0
				and 1.0. If not set the default score is 1.0.
			stopwords: Used to supply the index with a custom stopword list to be ignored
				during indexing and search time.
			temporary: Create a lightweight temporary index which will expire after the
				specified period of inactivity (in seconds). The internal idle timer is
				reset whenever the index is searched or added to. Because such indexes
				are lightweight, you can create thousands of such indexes without negative
				performance implications.

				Note:
					When creating temporary indexes consider also using
					`CreateFlags.SKIP_INITIAL_SCAN` to avoid costly scanning.
		"""
		command: List[Any] = [str(FullTextCommands.CREATE), name, str(CommandCreateParameters.ON), str(on)]
		if prefix is not None:
			prefix = tuple(prefix)
			command.extend([str(CommandCreateParameters.PREFIX), len(prefix), *prefix])
		if filter is not None:
			command.extend([str(CommandCreateParameters.FILTER), str(filter)])
		if language is not None:
			command.extend([str(CommandCreateParameters.LANGUAGE), str(language)])
		if language_field is not None:
			command.extend([str(CommandCreateParameters.LANGUAGE_FIELD), str(language_field)])
		if payload_field is not None:
			command.extend([str(CommandCreateParameters.PAYLOAD_FIELD), str(payload_field)])
		if score is not None:
			score = float(score)
			if score < 0 or score > 1:
				raise ValueError(f'score must be between 0.0 and 1.0, got {score}')
			command.extend([str(CommandCreateParameters.SCORE), str(score)])
		if score_field is not None:
			command.extend([str(CommandCreateParameters.SCORE_FIELD), str(score_field)])
		if stopwords is not None:
			stopwords = tuple(stopwords)
			command.extend([str(CommandCreateParameters.STOPWORDS), len(stopwords), *stopwords])
		if temporary is not None:
			command.extend([str(CommandCreateParameters.TEMPORARY), int(temporary)])
		if flags is not None:
			if CreateFlags.MAX_TEXT_FIELDS in flags:
				command.append(str(CommandCreateParameters.MAXTEXTFIELDS))
			if CreateFlags.NO_FIELDS in flags:
				command.append(str(CommandCreateParameters.NOFIELDS))
			if CreateFlags.NO_FREQUENCIES in flags:
				command.append(str(CommandCreateParameters.NOFREQS))
			if CreateFlags.NO_HIGHLIGHTS in flags:
				command.append(str(CommandCreateParameters.NOHL))
			if CreateFlags.NO_OFFSETS in flags:
				command.append(str(CommandCreateParameters.NOOFFSETS))
			if CreateFlags.SKIP_INITIAL_SCAN in flags:
				command.append(str(CommandCreateParameters.SKIPINITIALSCAN))

		command.append(str(CommandCreateParameters.SCHEMA))
		f: 'Field'
		x: Any
		command.extend([x for f in fields for x in f])
		LOG.debug(f'executing command: {" ".join(map(str, command))}')
		return self.execute(*command, error_func=_check_index_exists_error)

	async def get_document(
		self, index_name: str, /, document_id: str, *, document_cls: Optional[Type[Document]] = None
	) -> Union[Document, Dict[str, str]]:
		"""
		Retrieve the full contents of a document.

		Args:
			document_id: The id of the document as inserted into the index.
			document_cls: If supplied an instance of the supplied class will be returned
				loaded up with the returned data (`document_cls(**doc)`). Otherwise a
				dictionary is returned.
		"""
		command: List[str] = [str(FullTextCommands.GET), index_name, document_id]
		LOG.debug(f'executing command: {" ".join(command)}')
		raw: Optional[List[str]] = await self.execute(*command)
		if raw is None:
			raise DocumentNotFoundError(document_id)
		i: int
		mapped: Dict[str, str] = {raw[i]: raw[i + 1] for i in range(0, len(raw), 2)}
		if document_cls is not None:
			return document_cls(**mapped)
		return mapped

	async def info(self, index_name: str, /) -> IndexInfo:
		"""
		Returns information and statistics on the index. Returned values include:
			* number of documents
			* number of distinct terms
			* average bytes per record
			* size and capacity of the index buffers
		"""
		command: List[str] = [str(FullTextCommands.INFO), index_name]
		LOG.debug(f'executing command: {" ".join(command)}')
		try:
			res: List[Any] = await self.execute(*command)
		except ResponseError as ex:
			if str(ex).lower() == str(ErrorResponses.UNKNOWN_INDEX):
				raise UnknownIndexError(index_name)
			raise
		x: int
		mapped: Dict[str, Any] = {res[x]: res[x + 1] for x in range(0, len(res), 2)}
		return IndexInfo(**mapped)

	async def search(
		self,
		index_name: str,
		/,
		query: str,
		*,
		document_cls: Optional[Type[Document]] = None,
		expander: Optional[str] = None,
		flags: Optional[SearchFlags] = None,
		geo_filter: Optional[GeoFilter] = None,
		highlight: Optional[Highlight] = None,
		in_keys: Optional[Sequence[str]] = None,
		in_fields: Optional[Sequence[str]] = None,
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
			document_cls:
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
					`FTCommandsMixin.add_document`). The payloads follow the document id, and if
					`SearchFlags.WITH_SCORES` was set, follow the scores.
				* `SearchFlags.WITH_SCORES`: Return the relative internal score of each document.
					This can be used to merge results from multiple instances.
				* `SearchFlags.WITH_SORT_KEYS`: Only relevant in conjunction with `sort_by`.
					Returns the value of the sorting key, right after the id and score and/or
					payload if requested. This is usually not needed by users and exists for
					distributed search coordination purposes.
			geo_filter: Filter the results to a given radius from the supplied longitude and latitude.

				Note: Only applies to GEO fields.

				Note: It is also possible to apply geo filtering via the actual query.
					See https://oss.redislabs.com/redisearch/Query_Syntax/
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

				Note: Only applies to NUMERIC fields.

				Note: It is also possible to apply numeric filtering via the actual query.
					See https://oss.redislabs.com/redisearch/Query_Syntax/
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
		command: List[Any] = [str(FullTextCommands.SEARCH), index_name, repr(query)]
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
		raw_results: List[Any] = await self.execute(*command)
		total: int = raw_results[0]
		x: int
		y: int
		# massage the results into the following format:
		# [
		#   {
		#     'document_id': '<id>',
		#     'document': {
		#       '<field>': <value>,
		#       ...
		#     }
		#     ...
		#   }
		# ]
		formatted: List[Dict[str, Any]] = [
			dict(
				document_id=raw_results[x],
				document=dict(_document_cls=document_cls, **{
					raw_results[x + 1][y]: raw_results[x + 1][y + 1] for y in range(0, len(raw_results[x + 1]), 2)
				})
			)
			for x in range(1, len(raw_results[1:]), 2)
		]
		return SearchResult(documents=formatted, count=len(formatted), total=total, offset=offset, limit=limit_)


class FTCommandsMixin(RedicalBase):
	_ft: Commands

	@property
	def ft(self) -> Commands:
		"""
		Access *RediSearch* (full text) commands.
		"""
		return self._ft

	def __init__(self, resource: RedicalResource) -> None:
		super().__init__(resource)
		self._ft = Commands(resource)

	GeoFilter: ClassVar[Type[GeoFilter]] = GeoFilter
	Highlight: ClassVar[Type[Highlight]] = Highlight
	Languages: ClassVar[Type[Languages]] = Languages
	NumericFilter: ClassVar[Type[NumericFilter]] = NumericFilter
	ReplaceOptions: ClassVar[Type[ReplaceOptions]] = ReplaceOptions
	SearchFlags: ClassVar[Type[SearchFlags]] = SearchFlags
	Summarize: ClassVar[Type[Summarize]] = Summarize
