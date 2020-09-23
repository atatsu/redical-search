from typing import List

from redical import ResponseError

__all__: List[str] = [
	'DocumentExistsError',
	'DocumentNotFoundError',
	'IndexExistsError',
	'UnknownIndexError',
]


class DocumentExistsError(ResponseError):
	"""
	Raised when `RediSearch.add_document()` is called in non-replace mode and the
	document already exists.
	"""


class DocumentNotFoundError(ResponseError):
	"""
	Raised when `RediSearch.get_document()` is called with a document id that
	is not present in the index.
	"""


class IndexExistsError(ResponseError):
	"""
	Raised when `RediSearch.create_index()` is called and the index already exists.
	"""


class UnknownIndexError(ResponseError):
	"""
	Raised when `RediSearch.info()` is called and the index does not exist.
	"""
