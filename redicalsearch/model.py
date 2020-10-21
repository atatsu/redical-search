from typing import Any, Dict, List, Mapping, Sequence, Tuple, Type

from pydantic import root_validator, validator, BaseModel, Field

__all__: List[str] = ['Document', 'DocumentWrap', 'IndexInfo', 'SearchResult']


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
		mapped: Dict[str, str] = {v[x]: v[x + 1] for x in range(0, len(v), 2)}
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
	class Config:
		allow_mutation: bool = False


class DocumentWrap(BaseModel):
	id: str = Field(..., alias='document_id')
	# We technically allow subclasses of `Document` for `document` in place of a dict
	# but we're handling it in the root validator as it is being magically applied via
	# the `_document_cls` dict entry that gets added from `RediSearch.search()` via a kwarg.
	document: Dict[str, Any]

	@root_validator
	def check_model(cls, values: Mapping[str, Any]) -> Dict[str, Any]:
		v: Dict[str, Any] = dict(values)
		if 'document' not in v or '_document_cls' not in v['document']:
			return v

		if '_document_cls' in v['document'] and v['document']['_document_cls'] is None:
			del v['document']['_document_cls']
			return v

		doc_cls: Type[Document] = v['document']['_document_cls']
		v['document'] = doc_cls(**v['document'])
		return v

	class Config:
		allow_mutation: bool = False


class SearchResult(BaseModel):
	documents: List[DocumentWrap]
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

	class Config:
		allow_mutation: bool = False
