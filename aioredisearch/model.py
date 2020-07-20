from typing import Any, Dict, List, Sequence

from pydantic import validator, BaseModel, Field

__all__: List[str] = ['IndexInfo']


class IndexInfo(BaseModel):
	name: str = Field(..., alias='index_name')
	options: List[str] = Field(..., alias='index_options')
	field_defs: Dict[str, Dict[str, Any]] = Field(..., alias='fields')
	number_of_documents: int = Field(..., alias='num_docs')
	number_of_terms: int = Field(..., alias='num_terms')
	number_of_records: int = Field(..., alias='num_records')

	@validator('field_defs', pre=True)
	def format_field_defs(cls, v: Sequence[Sequence[str]]) -> Dict[str, Any]:
		print(v)
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
