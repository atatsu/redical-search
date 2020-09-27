from enum import auto, Flag
from typing import List

__all__: List[str] = ['CreateFlags']


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
