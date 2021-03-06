from __future__ import annotations

from abc import abstractmethod, ABC
from enum import auto, unique, Enum, Flag
from typing import (
	cast,
	Any,
	ClassVar,
	Dict,
	List,
	Mapping,
	Optional,
	Sequence,
	Tuple,
	Type,
	Union,
)

from .const import FieldParameters, FieldTypes
from .option import CreateFlags, Languages, Structures

__all__: List[str] = [
	'FieldFlags',
	'GeoField',
	'IndexOptions',
	'NumericField',
	'PhoneticMatchers',
	'Schema',
	'SchemaGeoField',
	'SchemaNumericField',
	'SchemaTagField',
	'SchemaTextField',
	'TagField',
	'TextField',
]


class FieldFlags(Flag):
	NO_INDEX = auto()
	"""
	Fields created using this flag will not be indexed. This is useful in conjunction with
	`FieldFlags.SORTABLE` to create fields whose update using `CommandAddParameters.PARTIAL` will
	not cause full reindexing of the document. If a field has `FieldFlags.NO_INDEX` and doesn't
	have `FieldFlags.SORTABLE` it will be ignored by the index.
	"""
	NO_STEM = auto()
	"""
	Disable stemming when indexing the field's values. This may be ideal for things like proper names.

	Note: Only applies to `TextField`s.
	"""
	SORTABLE = auto()
	"""
	Allows results to be sorted by the value of fields using this flag (this adds memory overhead
	so *do not* declare it on large text fields).

	Note: Only applies to `NumericField`s, `TextField`s, and `TagField`s.
	"""


@unique
class PhoneticMatchers(Enum):
	ENGLISH: str = 'dm:en'
	FRENCH: str = 'dm:fr'
	PORTUGUESE: str = 'dm:pt'
	SPANISH: str = 'dm:es'

	def __str__(self) -> str:
		return str(self.value)


class Field(List[Any]):
	def __init__(self, name: str, /) -> None:
		super().__init__()
		self.append(name)


class GeoField(Field):
	"""
	Defines a geo-indexing field in a schema definition.

	Note:
		When adding documents geo format is *x,y*, or *longitude,latitude*.

	Args:
		name: A name for this field.
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
	"""
	def __init__(self, name: str, /, flags: Optional[FieldFlags] = None) -> None:
		super().__init__(name)
		self.append(str(FieldTypes.GEO))
		if flags is not None and FieldFlags.NO_INDEX in flags:
			self.append(str(FieldParameters.NOINDEX))

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX


class NumericField(Field):
	"""
	Defines a numeric field in a schema definition.

	Args:
		name: A name for this field.
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
	"""
	def __init__(self, name: str, /, flags: Optional[FieldFlags] = None) -> None:
		super().__init__(name)
		self.append(str(FieldTypes.NUMERIC))
		if flags is not None:
			if FieldFlags.SORTABLE in flags:
				self.append(str(FieldParameters.SORTABLE))
			if FieldFlags.NO_INDEX in flags:
				self.append(str(FieldParameters.NOINDEX))

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class TagField(Field):
	"""
	Defines a tag field in a schema definition.

	Args:
		name: A name for this field.
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
		separator: Indicates how the text contained in this field is to be split into
			individual tags. The value **must** be a single character.

			Note: Defaults to `,`.
	"""
	def __init__(self, name: str, /, flags: Optional[FieldFlags] = None, *, separator: Optional[str] = None) -> None:
		super().__init__(name)
		self.append(str(FieldTypes.TAG))
		if separator is not None:
			if len(separator) > 1:
				raise ValueError(f'Separator longer than one character: {separator!r}')
			self.extend([str(FieldParameters.SEPARATOR), separator])
		if flags is not None:
			if FieldFlags.SORTABLE in flags:
				self.append(str(FieldParameters.SORTABLE))
			if FieldFlags.NO_INDEX in flags:
				self.append(str(FieldParameters.NOINDEX))

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class TextField(Field):
	"""
	Defines a text field in a schema definition.

	Args:
		name: A name for this field.
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.NO_STEM` - If set will disable stemming (adding the base form of a word
				to the index). In other words, if set this field will only support exact,
				word-for-word matches.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
		phonetic_matcher: If supplied this field will have phonetic matching on it in
			searches by default. The passed argument specifies the phonetic algorithm and
			language used. The following matchers are supported:
				* `PhoneticMatchers.ENGLISH`
				* `PhoneticMatchers.FRENCH`
				* `PhoneticMatchers.PORTUGUESE`
				* `PhoneticMatchers.SPANISH`
		weight: Declares the importance of this field when calculating result accuracy. Defaults to
			`1` if not specified.

			Note: This is a multiplication factor.
	"""
	def __init__(
		self,
		name: str,
		/,
		flags: Optional[FieldFlags] = None,
		*,
		phonetic_matcher: Optional[PhoneticMatchers] = None,
		weight: Optional[Union[int, float]] = None
	) -> None:
		super().__init__(name)
		self.append(str(FieldTypes.TEXT))

		if flags is not None and FieldFlags.NO_STEM in flags:
			self.append(str(FieldParameters.NOSTEM))
		if weight is not None:
			self.extend([str(FieldParameters.WEIGHT), float(weight)])
		# could do an `isinstance` check here...
		if phonetic_matcher is not None:
			self.extend([str(FieldParameters.PHONETIC), str(phonetic_matcher)])
		if flags is not None:
			if FieldFlags.SORTABLE in flags:
				self.append(str(FieldParameters.SORTABLE))
			if FieldFlags.NO_INDEX in flags:
				self.append(str(FieldParameters.NOINDEX))

	PhoneticMatchers: ClassVar[Type[PhoneticMatchers]] = PhoneticMatchers
	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	NO_STEM: ClassVar[FieldFlags] = FieldFlags.NO_STEM
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class SchemaField(ABC):
	name: str

	@abstractmethod
	def field(self) -> Field:
		pass

	def __set_name__(self, owner: Type[Any], name: str) -> None:
		self.name = name


class SchemaGeoField(SchemaField):
	"""
	Defines a geo-indexing field in a schema definition class.

	Args:
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
	"""
	flags: Optional[FieldFlags]

	def __init__(self, flags: Optional[FieldFlags] = None) -> None:
		self.flags = flags

	def field(self) -> Field:
		return GeoField(self.name, flags=self.flags)

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX


class SchemaNumericField(SchemaField):
	"""
	Defines a numeric field in a schema definition class.

	Args:
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
	"""
	flags: Optional[FieldFlags]

	def __init__(self, flags: Optional[FieldFlags] = None) -> None:
		self.flags = flags

	def field(self) -> Field:
		return NumericField(self.name, flags=self.flags)

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class SchemaTagField(SchemaField):
	"""
	Defines a tag field in a schema definition class.

	Args:
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
		separator: Indicates how the text contained in this field is to be split into
			individual tags. The value **must** be a single character.

			Note: Defaults to `,`.
	"""
	flags: Optional[FieldFlags]
	separator: Optional[str]

	def __init__(
		self,
		flags: Optional[FieldFlags] = None,
		*,
		separator: Optional[str] = None
	) -> None:
		self.flags = flags
		self.separator = separator

	def field(self) -> Field:
		return TagField(self.name, flags=self.flags, separator=self.separator)

	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class SchemaTextField(SchemaField):
	"""
	Defines a text field in a schema definition.

	Args:
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.NO_STEM` - If set will disable stemming (adding the base form of a word
				to the index). In other words, if set this field will only support exact,
				word-for-word matches.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
		phonetic_matcher: If supplied this field will have phonetic mathing on it in
			searches by default. The passed argument specifies the phonetic algorithm and
			language used. The following matchers are supported:
				* `PhoneticMatchers.ENGLISH`
				* `PhoneticMatchers.FRENCH`
				* `PhoneticMatchers.PORTUGUESE`
				* `PhoneticMatchers.SPANISH`
		weight: Declares the importance of this field when calculating result accuracy. Defaults to
			`1` if not specified.

			Note: This is a multiplication factor.
	"""
	flags: Optional[FieldFlags]
	phonetic_matcher: Optional[PhoneticMatchers]
	weight: Optional[Union[int, float]]

	def __init__(
		self,
		flags: Optional[FieldFlags] = None,
		*,
		phonetic_matcher: Optional[PhoneticMatchers] = None,
		weight: Optional[Union[int, float]] = None
	) -> None:
		self.flags = flags
		self.phonetic_matcher = phonetic_matcher
		self.weight = weight

	def field(self) -> Field:
		return TextField(self.name, flags=self.flags, phonetic_matcher=self.phonetic_matcher, weight=self.weight)

	PhoneticMatchers: ClassVar[Type[PhoneticMatchers]] = PhoneticMatchers
	NO_INDEX: ClassVar[FieldFlags] = FieldFlags.NO_INDEX
	NO_STEM: ClassVar[FieldFlags] = FieldFlags.NO_STEM
	SORTABLE: ClassVar[FieldFlags] = FieldFlags.SORTABLE


class IndexOptions:
	"""
	Include with a schema definition class to control additional behaviors
	of the created index. Available options include:
		* `on`
		* `prefixes`
		* `filter`
		* `flags`
		* `language`
		* `language_field`
		* `payload_field`
		* `score`
		* `score_field`
		* `stopwords`
		* `temporary`

	Example:
		class MySchema(Schema):
			class Options(IndexOptions):
				prefixes = ('myindex:',)
				flags = CreateFlags.NO_FREQUENCIES | CreateFlags.NO_HIGHLIGHTS
				temporary = 600
	"""
	on: ClassVar[Structures] = Structures.HASH
	"""
	Currently only supports `Structures.HASH` (default).
	"""
	prefixes: ClassVar[Optional[Sequence[str]]] = None
	"""
	Tells the index which keys it should index. You can add several prefixes
	to the index. Since the argument is optional, the default is `*` (all keys).
	"""
	filter: ClassVar[Optional[str]] = None
	"""
	Supply a filter expression with the full *RediSearch* aggregation expression
	language. It is possible to use `@__key` to access the key that was just
	added/changed. A field can be used to set field name by passing
	`FILTER @indexName=="myindexname"`.
	"""
	flags: ClassVar[Optional[CreateFlags]] = None
	language: ClassVar[Optional[Languages]] = None
	"""
	If set indicates the default language for documents in the index.
	Defaults to `Languages.ENGLISH`.
	"""
	language_field: ClassVar[Optional[str]] = None
	"""
	If set indicates the document field that should be used as the document language.
	"""
	payload_field: ClassVar[Optional[str]] = None
	"""
	If set indicates the document field that should be used as a binary safe
	payload string to the document that can be evaluated at query time by a custom
	scoring function, or retrieved to the client.
	"""
	score: ClassVar[Optional[Union[float, int]]] = None
	"""
	If set indicates the default score for documents in the index.
	Default score is `1.0`.
	"""
	score_field: ClassVar[Optional[str]] = None
	"""
	If set indicates the document field that should be used as the document's rank
	based on the user's ranking. Ranking must be between `0.0` and `1.0`. If not
	set the default score is `1`.
	"""
	stopwords: ClassVar[Optional[Sequence[str]]] = None
	"""
	If supplied the index is set with a custom stopword list to be ignored during
	indexing and search time.
	"""
	temporary: ClassVar[Optional[int]] = None
	"""
	Create a lightweight temporary index which will expire after the specified period
	of inactivity (in seconds). The internal idle timer is reset whenever the index
	is searched or added to. Because such indexes are lightweight you can create
	thousands of such indexes without negative performance implications and therefore
	you should consider using `CreateFlags.SKIP_INITIAL_SCAN` to avoid costly
	scanning.
	"""


class SchemaMeta(type):
	__fields__: Tuple[str, ...]

	def __new__(
		meta: Type[SchemaMeta], name: str, bases: Tuple[type, ...], ns: Mapping[str, Any], **kwargs: Any
	) -> SchemaMeta:
		new_ns: Dict[str, Any] = dict(ns)
		fields: List[str] = []

		attr_name: str
		attr_value: Any

		base: Type[Any]
		for base in bases:
			if not issubclass(base, Schema):
				continue
			for attr_name, attr_value in vars(base).items():
				if not isinstance(attr_value, SchemaField):
					continue
				fields.append(attr_name)

		for attr_name, attr_value in new_ns.items():
			if not isinstance(attr_value, SchemaField):
				continue
			fields.append(attr_name)

		new_ns['__fields__'] = tuple(fields)
		return cast(SchemaMeta, super().__new__(cast(Type[type], meta), name, bases, new_ns))


class Schema(metaclass=SchemaMeta):
	Options: ClassVar[Type[IndexOptions]]
	__fields__: ClassVar[Tuple[str]]

	@classmethod
	def _get_fields(cls) -> List[Field]:
		field_name: str
		fields: List[Field] = []
		for field_name in cls.__fields__:
			schema_field: SchemaField = getattr(cls, field_name)
			fields.append(schema_field.field())
		return fields

	@classmethod
	def _get_options(cls) -> Dict[str, Any]:
		opt_cls: IndexOptions = getattr(cls, 'Options', IndexOptions)
		options: Dict[str, Any] = dict(
			on=opt_cls.on,
			prefixes=opt_cls.prefixes,
			filter=opt_cls.filter,
			flags=opt_cls.flags,
			language=opt_cls.language,
			language_field=opt_cls.language_field,
			payload_field=opt_cls.payload_field,
			score=opt_cls.score,
			score_field=opt_cls.score_field,
			stopwords=opt_cls.stopwords,
			temporary=opt_cls.temporary,
		)
		return options
