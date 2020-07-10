from enum import unique, Enum
from typing import Any, List, Iterable, Optional, Sequence, Tuple, Union, TYPE_CHECKING

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


class Field:
	_parameters: Tuple[Any, ...]
	_name: str

	def __init__(self, name: str, /, *parameters: Any) -> None:
		self._name = name
		self._parameters = parameters

	def __iter__(self) -> Iterable[Any]:
		return iter(list((self._name, *self._parameters)))


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
		if sortable:
			parameters.append(str(FieldParameters.SORTABLE))
		if no_index:
			parameters.append(str(FieldParameters.NOINDEX))

		if not sortable and no_index:
			raise ValueError('Fields must be sortable or be indexed')
		super().__init__(name, *parameters)


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
		if sortable:
			parameters.append(str(FieldParameters.SORTABLE))
		if no_index:
			parameters.append(str(FieldParameters.NOINDEX))

		if not sortable and no_index:
			raise ValueError('Fields must be sortable or be indexed')
		super().__init__(name, *parameters)


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
		if sortable:
			parameters.append(str(FieldParameters.SORTABLE))
		if no_index:
			parameters.append(str(FieldParameters.NOINDEX))

		if not sortable and no_index:
			raise ValueError('Fields must be sortable or be indexed')
		super().__init__(name, *parameters)


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
		if sortable:
			parameters.append(str(FieldParameters.SORTABLE))
		if no_index:
			parameters.append(str(FieldParameters.NOINDEX))

		if not sortable and no_index:
			raise ValueError('Fields must be sortable or be indexed')
		super().__init__(name, *parameters)


@unique
class FullTextCommands(Enum):
	CREATE: str = 'FT.CREATE'

	def __str__(self) -> str:
		return str(self.value)


@unique
class CommandCreateParameters(Enum):
	NOOFFSETS: str = 'NOOFFSETS'
	NOFIELDS: str = 'NOFIELDS'
	STOPWORDS: str = 'STOPWORDS'

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
		no_term_offsets: bool = False,
		no_field_flags: bool = False,
		stopwords: Optional[Sequence[str]] = None
	) -> None:
		"""
		Creates an index with the given spec.
		"""
		# command_args: List[Any] = [str(FullTextCommands.CREATE), self._index_name]
		# if no_term_offsets:
		#     command_args.append(str(CommandCreateParameters.NOOFFSETS))
		# if no_field_flags:
		#     command_args.append(str(CommandCreateParameters.NOFIELDS))
		# if stopwords is not None:
		#     command_args.extend([str(CommandCreateParameters.STOPWORDS), len(stopwords)])
		#     if len(stopwords) > 0:
		#         command_args.extend(stopwords)
		# command_args.append(SCHEMA)
		# f: Field
		# command_args.extend(list(chain(*[f.parameters for f in fields])))
		# return await self._redis.execute_command(*command_args)
