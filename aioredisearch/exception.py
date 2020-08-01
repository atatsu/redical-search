from typing import List

from aredis import ResponseError  # type: ignore

__all__: List[str] = [
	'DocumentExistsError',
	'IndexExistsError',
	'UnknownIndexError',
]


class DocumentExistsError(ResponseError):
	"""
	Raised when `RediSearch.add_document()` is called in non-replace mode and the
	document already exists.
	"""


class IndexExistsError(ResponseError):
	"""
	Raised when `RediSearch.create_index()` is called and the index already exists.
	"""


class UnknownIndexError(ResponseError):
	"""
	Raised when `RediSearch.info()` is called and the index does not exist.
	"""
