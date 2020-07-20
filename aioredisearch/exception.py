from typing import List

from aredis import ResponseError  # type: ignore

__all__: List[str] = [
	'DocumentExists',
	'IndexExists',
	'UnknownIndex',
]


class DocumentExists(ResponseError):
	"""
	Raised when `RediSearch.add_document()` is called in non-replace mode and the
	document already exists.
	"""


class IndexExists(ResponseError):
	"""
	Raised when `RediSearch.create_index()` is called and the index already exists.
	"""


class UnknownIndex(ResponseError):
	"""
	Raised when `RediSearch.info()` is called and the index does not exist.
	"""
