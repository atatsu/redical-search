"""
A module for housing all the various non-primitive options that can be passed
to the various methods provided by the `Commands` mixin class.
"""
from enum import auto, unique, Enum, Flag
from typing import ClassVar, List, Optional, Sequence, Type

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

__all__: List[str] = [
	'CreateFlags',
	'Geo',
	'GeoFilter',
	'GeoFilterUnits',
	'Highlight',
	'Languages',
	'NumericFilter',
	'NumericFilterFlags',
	'SearchFlags',
	'Structures',
	'Summarize',
]


class CreateFlags(Flag):
	MAX_TEXT_FIELDS = auto()
	"""
	For efficiency *RediSearch* encodes indexes differently if they are created with
	less than 32 text fields. This flag forces *RediSearch* to encode indexes as if
	there were more than 32 text fields, which allows you to add additional fields
	(beyond 32) using `ft.alter`.
	"""
	NO_FIELDS = auto()
	"""
	If used no field bits will be stored for each term.
	Saves memory but does not allow filtering by specific fields.
	"""
	NO_FREQUENCIES = auto()
	"""
	If used term frequencies will not be stored on the index.
	This saves memory but does not allow sorting based on the frequencies of a
	given term within documents.
	"""
	NO_HIGHLIGHTS = auto()
	"""
	If used highlighting support will be disabled on the index.
	Conserves storage space and memory by not storing corresponding byte offsets for
	term positions.

	Note: Implied by `CreateFlags.NO_OFFSETS`.
	"""
	NO_OFFSETS = auto()
	"""
	If used no term offsets will be stored for documents.
	Saves memory but does not allow exact searches or highlighting.

	Note: Implies `CreateFlags.NO_HIGHLIGHTS`.
	"""
	SKIP_INITIAL_SCAN = auto()
	"""
	If used there is no initial scan and indexing performed when the index is created.
	"""


@dataclass
class Geo:
	latitude: float
	longitude: float

	def __str__(self) -> str:
		return f'{self.longitude},{self.latitude}'


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


class NumericFilterFlags(Flag):
	EXCLUSIVE_MAX = auto()
	EXCLUSIVE_MIN = auto()


class NumericFilter(BaseModel):
	Flags: ClassVar[Type[NumericFilterFlags]] = NumericFilterFlags

	field: str
	maximum: Optional[float]
	minimum: Optional[float]
	flags: Optional[NumericFilterFlags]


class SearchFlags(Flag):
	EXPLAIN_SCORE = auto()
	IN_ORDER = auto()
	NO_CONTENT = auto()
	VERBATIM = auto()
	NO_STOPWORDS = auto()
	WITH_SCORES = auto()
	WITH_PAYLOADS = auto()
	WITH_SORT_KEYS = auto()
	# SORTBY flags
	ASC = auto()
	"""
	Sort search results in ascending order.
	"""
	DESC = auto()
	"""
	Sort search results in descending order.
	"""


@unique
class Structures(Enum):
	HASH: str = 'HASH'

	def __str__(self) -> str:
		return str(self.value)


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
