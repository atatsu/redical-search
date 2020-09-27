from enum import auto, unique, Enum, Flag
from typing import Any, ClassVar, List, Optional, Type, Union

from .const import FieldParameters, FieldTypes

__all__: List[str] = [
	'FieldFlags',
	'GeoField',
	'NumericField',
	'PhoneticMatchers',
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
	Args:
		name: A name for this field.
		flags: The following flags are accepted:
			* `FieldFlags.NO_INDEX` - If set this field will not be indexed.
			* `FieldFlags.SORTABLE` - If set search results may be sorted by the value
				of this field.
		separator: Indicates how the text contained in this field is to be split into
			individual tags. The value **must** be a single character.
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
