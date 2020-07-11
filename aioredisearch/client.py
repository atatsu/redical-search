from __future__ import annotations

from enum import unique, Enum
from typing import Any, List, Optional, Sequence, Union, TYPE_CHECKING

if TYPE_CHECKING:
	from aredis import StrictRedis  # type: ignore


SCHEMA: str = 'SCHEMA'
VALID_PHONETIC_MATCHERS: List[str] = ['dm:en', 'dm:fr', 'dm:pt', 'dm:es']


@unique
class FieldTypes(Enum):
	GEO: str = 'GEO'
	NUMERIC: str = 'NUMERIC'
	TAG: str = 'TAG'
	TEXT: str = 'TEXT'

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


class Field(List[str]):
	def __init__(self, name: str, /, *parameters: Any, no_index: bool = False, sortable: bool = False) -> None:
		super().__init__()
		if not sortable and no_index:
			raise ValueError('Fields must be sortable or be indexed')

		param: Any
		_parameters: List[str] = list([str(param) for param in parameters])

		if sortable:
			_parameters.append(str(FieldParameters.SORTABLE))
		if no_index:
			_parameters.append(str(FieldParameters.NOINDEX))

		self.append(name)
		self.extend(_parameters)


class GeoField(Field):
	"""
	Defines a geo-indexing field in a schema definition.

	Args:
		name: A name for this field.
		no_index: If set this field will not be indexed.
		sortable: If set allows the results to be sorted by the value of this field.
	"""
	def __init__(self, name: str, /, *, no_index: bool = False, sortable: bool = False) -> None:
		parameters: List[str] = [str(FieldTypes.GEO)]
		super().__init__(name, *parameters, no_index=no_index, sortable=sortable)


class NumericField(Field):
	"""
	Defines a numeric field in a schema definition.

	Args:
		name: A name for this field.
		no_index: If set this field will not be indexed.
		sortable: If set allows the results to be sorted by the value of this field.
	"""
	def __init__(self, name: str, /, *, no_index: bool = False, sortable: bool = False) -> None:
		parameters: List[str] = [str(FieldTypes.NUMERIC)]
		super().__init__(name, *parameters, no_index=no_index, sortable=sortable)


class TagField(Field):
	"""
	Args:
		name: A name for this field.
		no_index: If set this field will not be indexed.
		separator: Indicates how the text contained in this field is to be split into
			individual tags. The value **must** be a single character.
		sortable: If set allows the results to be sorted by the value of this field.
	"""
	def __init__(
		self, name: str, /, *, no_index: bool = False, separator: Optional[str] = None, sortable: bool = False
	) -> None:
		parameters: List[str] = [str(FieldTypes.TAG)]
		if separator is not None:
			if len(separator) > 1:
				raise ValueError(f'Separator longer than one character: {separator!r}')
			parameters.extend([str(FieldParameters.SEPARATOR), separator])
		super().__init__(name, *parameters, no_index=no_index, sortable=sortable)


class TextField(Field):
	"""
	Defines a text field in a schema definition.

	Args:
		name: A name for this field.
		no_index: If set this field will not be indexed.
		no_stem: If set will disable stemming (adding the base form of a word to the index).
			In other words, if set this field will only support exact, word-for-word
			matches.
		phonetic_matcher: If supplied this field will have phonetic matching on it in
			searches by default. The passed argument specifies the phonetic algorithm and
			language used. The following matchers are supported:
				* dm:en - Double Metaphone for English
				* dm:fr - Double Metaphone for French
				* dm:pt - Double Metaphone for Portuguese
				* dm:es - Double Metaphone for Spanish
		sortable: If set allows the results to be sorted by the value of this field (adds
			memory overhead, do not use on large text fields).
		weight: The importance of this field when calculating result accuracy. Defaults
			to `1` if not specified.
	"""
	def __init__(
		self,
		name: str,
		/,
		*,
		no_index: bool = False,
		no_stem: bool = False,
		phonetic_matcher: Optional[str] = None,
		sortable: bool = False,
		weight: Optional[Union[int, float]] = None
	) -> None:
		parameters: List[Any] = [str(FieldTypes.TEXT)]
		if no_stem:
			parameters.append(str(FieldParameters.NOSTEM))
		if weight is not None:
			parameters.extend([str(FieldParameters.WEIGHT), weight])
		if phonetic_matcher is not None:
			if phonetic_matcher not in VALID_PHONETIC_MATCHERS:
				raise ValueError(f'Invalid phonetic matcher: {phonetic_matcher!r}')
			parameters.extend([str(FieldParameters.PHONETIC), phonetic_matcher])
		super().__init__(name, *parameters, no_index=no_index, sortable=sortable)


@unique
class FullTextCommands(Enum):
	CREATE: str = 'FT.CREATE'

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
	TEMPORARY: str = 'TEMPORARY'

	def __str__(self) -> str:
		return str(self.value)


class RediSearch:
	"""
	"""
	_index_name: str
	_redis: 'StrictRedis'

	@property
	def redis(self) -> 'StrictRedis':
		return self._redis

	def __init__(self, index_name: str, /, *, redis: 'StrictRedis') -> None:
		self._index_name = index_name
		self._redis = redis

	async def create_index(
		self,
		*fields: Field,
		max_text_fields: bool = False,
		no_fields: bool = False,
		no_frequencies: bool = False,
		no_highlights: bool = False,
		no_offsets: bool = False,
		stopwords: Optional[Sequence[str]] = None,
		temporary: Union[float, int] = 0,
	) -> None:
		"""
		Creates an index with the given spec. The index name will be used in all the
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
				will be stored for term positions. Implied by `no_offsets`.
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
		command_args: List[Any] = [str(FullTextCommands.CREATE), self._index_name]
		if max_text_fields:
			command_args.append(str(CommandCreateParameters.MAXTEXTFIELDS))
		if temporary > 0:
			command_args.extend([str(CommandCreateParameters.TEMPORARY), str(temporary)])
		if no_offsets:
			command_args.append(str(CommandCreateParameters.NOOFFSETS))
		if no_highlights:
			command_args.append(str(CommandCreateParameters.NOHL))
		if no_fields:
			command_args.append(str(CommandCreateParameters.NOFIELDS))
		if no_frequencies:
			command_args.append(str(CommandCreateParameters.NOFREQS))
		if stopwords is not None:
			num: str = str(len(stopwords))
			command_args.extend([str(CommandCreateParameters.STOPWORDS), num, *stopwords])
		command_args.append(SCHEMA)
		f: Field
		x: Any
		command_args.extend([x for f in fields for x in f])
		return await self._redis.execute_command(*command_args)
