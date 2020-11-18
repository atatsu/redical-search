from datetime import datetime
from typing import cast, Any, Dict, Generic, List, Mapping, Sequence, Tuple, Type, TypeVar, Union, TYPE_CHECKING

from pydantic import root_validator, validator, BaseModel, Field

if TYPE_CHECKING:
	from pydantic.fields import ModelField
	from pydantic.typing import AbstractSetIntStr, MappingIntStrAny

__all__: List[str] = ['Document', 'IndexInfo', 'SearchResult']


class IndexDefinition(BaseModel):
	prefixes: Tuple[str, ...]


class IndexInfo(BaseModel):
	name: str = Field(..., alias='index_name')
	definition: IndexDefinition = Field(..., alias='index_definition')
	options: List[str] = Field(..., alias='index_options')
	# FIXME: `BaseModel.fields` is being deprecated in favor of `BaseModel.__fields__`;
	#        once it is actually removed `field_defs` can be renamed to `fields` and the
	#        alias can be removed.
	field_defs: Dict[str, Dict[str, Any]] = Field(..., alias='fields')
	hash_indexing_failures: int
	number_of_documents: int = Field(..., alias='num_docs')
	number_of_terms: int = Field(..., alias='num_terms')
	number_of_records: int = Field(..., alias='num_records')
	percent_indexed: float

	@validator('definition', pre=True)
	def format_definition(cls, v: Sequence[str]) -> IndexDefinition:
		x: int
		mapped: Dict[str, Any] = {v[x]: v[x + 1] for x in range(0, len(v), 2)}
		prefix: str
		mapped['prefixes'] = [prefix for prefix in mapped['prefixes'] if prefix != '']
		return IndexDefinition(**mapped)

	@validator('field_defs', pre=True)
	def format_field_defs(cls, v: Sequence[Sequence[str]]) -> Dict[str, Any]:
		field_defs: Dict[str, Any] = {}
		field_def: Sequence[str]
		for field_def in v:
			field_name: str = field_def[0]
			field_type: str = field_def[2]
			field_options: List[str] = list(field_def[3:])
			field_defs[field_name] = dict(
				type=field_type,
				options=field_options
			)
		return field_defs

	class Config:
		allow_mutation: bool = False


class Document(BaseModel):
	id: str

	def hset(
		self,
		*,
		by_alias: bool = False,
		exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
		exclude_defaults: bool = False,
		exclude_unset: bool = False,
		include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
	) -> Dict[str, Any]:
		"""
		A convenience method for converting this document into a dictionary suitable
		for use in `Redical#hset`. A number of niceties are also performed on the
		underlying data:
			* Any `None` values will have their corresponding keys removed from the resulting
				dictionary
			* Any `bool` values will be converted to integers in the resulting dictionary
			* Any `datetime` values will be converted to unix timestamps (milliseconds)
			* The `id` attribute is removed from the resulting dictionary

		Note: All keyword parameters are the same as those for pydantic's `BaseModel#dict`.

		Args:
			by_alias: Whether field aliases should be used as keys in the resulting dictionary.
			exclude: Fields to exclude from the resulting dictionary.
			exclude_defaults: Whether fields which are equal to their default values should
				be excluded from the resulting dictionary.
			exclude_unset: Whether fields which were not explicitly set should be excluded
				from the resulting dictionary.
			include: Fields to include in the resulting dictionary.

		Returns:
			A copy of this document in dictionary form.
		"""
		d: Dict[str, Any] = super().dict(
			by_alias=by_alias,
			exclude=exclude,
			exclude_defaults=exclude_defaults,
			exclude_none=True,
			exclude_unset=exclude_unset,
			include=include
		)
		attr: str
		field: 'ModelField'
		for attr, field in self.__fields__.items():
			if attr in d and issubclass(field.type_, bool):
				d[attr] = int(d[attr])
				continue
			if attr in d and issubclass(field.type_, datetime):
				# FIXME: Maybe don't do this if the datetime is naive?
				d[attr] = int(d[attr].timestamp() * 1000)
				continue
		del d['id']
		return d


T = TypeVar('T')


class SearchResult(Generic[T], BaseModel):
	documents: List[T]
	"""
	The documents returned by the query.
	"""
	count: int
	"""
	The number of results contained within this result object.
	"""
	limit: int = 0
	"""
	The limit count applied while limiting the returned results of the query.
	"""
	offset: int = 0
	"""
	The offset applied while limiting the returned results of the query.
	"""
	total: int
	"""
	The total number of results based on the executed query.
	"""

	@root_validator(pre=True)
	def check_model(cls, values: Mapping[str, Any]) -> Dict[str, Any]:
		v: Dict[str, Any] = dict(values)
		docs: List[Union[T, Dict[str, Any]]] = []
		raw_docs: List[Dict[str, Any]] = v['documents']
		raw_doc: Dict[str, Any]
		for raw_doc in raw_docs:
			if '_document_cls' not in raw_doc or raw_doc['_document_cls'] is None:
				raw_doc.pop('_document_cls', None)
				docs.append(raw_doc)
				continue
			doc_cls: Type[Document] = raw_doc.pop('_document_cls')
			instance: Document = doc_cls(**raw_doc)
			docs.append(cast(T, instance))
		v['documents'] = docs
		return v

	class Config:
		allow_mutation: bool = False
