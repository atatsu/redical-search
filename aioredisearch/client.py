from __future__ import annotations

import logging
from enum import unique, Enum, IntFlag
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union, TYPE_CHECKING

from aredis import ResponseError  # type: ignore

from .exception import DocumentExists, IndexExists, UnknownIndex
from .model import IndexInfo

if TYPE_CHECKING:
	from aredis import StrictRedis  # type: ignore
	from .field import Field as BaseField
	Field = TypeVar('Field', bound=BaseField)


__all__: List[str] = ['RediSearch']

LOG: logging.Logger = logging.getLogger(__name__)


@unique
class ErrorResponses(Enum):
	DOCUMENT_ALREADY_EXISTS: str = 'document already exists'
	INDEX_ALREADY_EXISTS: str = 'index already exists'
	UNKNOWN_INDEX: str = 'unknown index name'

	def __str__(self) -> str:
		return str(self.value)


@unique
class FullTextCommands(Enum):
	ADD: str = 'FT.ADD'
	CREATE: str = 'FT.CREATE'
	INFO: str = 'FT.INFO'

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


class ReplaceOptions(IntFlag):
	DEFAULT: int = 4
	PARTIAL: int = 2
	NO_CREATE: int = 1


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
					* arabic
					* chinese
					* danish
					* dutch
					* english
					* finnish
					* french
					* german
					* hungarian
					* italian
					* norwegian
					* portuguese
					* romanian
					* russian
					* spanish
					* swedish
					* tamil
					* turkish

				Note:
					If indexing a Chinese language document the language **must** be set to 'chinese'
					in order for the Chinese characters to be tokenized properly.
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

	Languages: ClassVar[Type[Languages]] = Languages
	ReplaceOptions: ClassVar[Type[ReplaceOptions]] = ReplaceOptions

	async def create_index(
		self,
		*fields: 'Field',
		max_text_fields: bool = False,
		no_fields: bool = False,
		no_frequencies: bool = False,
		no_highlights: bool = False,
		no_offsets: bool = False,
		stopwords: Optional[Sequence[str]] = None,
		temporary: Union[float, int] = 0,
	) -> None:
		"""
		Create an index with the given spec. The index name will be used in all the
		key names so keep it short!

		Args:
			fields: A sequence of fields for the index
			max_text_fields: If set will force RediSearch to encode indexes as if there
				were more than 32 text fields, which allows for adding additional fields
				(beyond 32) using `RediSearch.alter_schema_add()`.
				For efficiency RediSearch encodes indexes differently if they are
				created with less than 32 text fields.
			no_fields: If set no field bits will be stored for each term. Saves memory
				but does not allow filtering by specific fields.
			no_frequencies: If set term frequencies will not be stored on the index. This
				saves memory but does not allow sorting based on the frequencies of a
				given term within documents.
			no_highlights: If set highlighting support will be disabled which
				conserves storage space and memory. No corresponding byte offsets
				will be stored for term positions.

				Implied by `no_offsets`.
			no_offsets: If set no term offsets will be stored for documents.
				Saves memory but does not allow exact searches or highlighting.

				Implies `no_highlights`.
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
		if max_text_fields:
			command.append(str(CommandCreateParameters.MAXTEXTFIELDS))
		if temporary > 0:
			command.extend([str(CommandCreateParameters.TEMPORARY), str(temporary)])
		if no_offsets:
			command.append(str(CommandCreateParameters.NOOFFSETS))
		if no_highlights:
			command.append(str(CommandCreateParameters.NOHL))
		if no_fields:
			command.append(str(CommandCreateParameters.NOFIELDS))
		if no_frequencies:
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
