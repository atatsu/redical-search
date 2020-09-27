from typing import List

from redical import ResponseError

__all__: List[str] = [
	'DocumentExistsError',
	'DocumentNotFoundError',
	'IndexExistsError',
	'UnknownIndexError',
]


# TODO: Nuke this
class DocumentExistsError(ResponseError):
	"""
	Raised when `FTCommandsMixin.add_document()` is called in non-replace mode and the
	document already exists.
	"""


# TODO: Nuke this
class DocumentNotFoundError(ResponseError):
	"""
	Raised when `FTCommandsMixin.get_document()` is called with a document id that
	is not present in the index.
	"""


# XXX: The docs claim that multiple calls to `ft.create` will just overwrite the spec...
#      but it's still replying with an error and the spec has most certainly *not* been
#      overwritten. So... maybe this will eventually not result in an error?
class IndexExistsError(ResponseError):
	"""
	Raised when `Redical.ft.create()` is called and the index already exists.
	"""


class UnknownIndexError(ResponseError):
	"""
	Raised when `FTCommandsMixin.info()` is called and the index does not exist.
	"""
