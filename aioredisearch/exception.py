from typing import List

from aredis import ResponseError  # type: ignore

__all__: List[str] = [
	'IndexExists',
]


class IndexExists(ResponseError):
	"""
	Raised when `RediSearch.create_index()` is called an the index already exists.
	"""
