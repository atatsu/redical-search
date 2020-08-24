import pytest  # type: ignore

from aioredisearch import Document, DocumentNotFoundError


@pytest.mark.integration
@pytest.mark.asyncio
async def test_no_document_cls(client_with_index):
	raw = dict(username='auser', real_name='A User', foo='bar')
	await client_with_index.add_document('auser', *raw.items())
	doc = await client_with_index.get_document('auser')
	assert raw == doc


@pytest.mark.integration
@pytest.mark.asyncio
async def test_doc_not_exist(client_with_index):
	with pytest.raises(DocumentNotFoundError) as cm:
		await client_with_index.get_document('auser')
	assert 'auser' == str(cm.value)


class User(Document):
	username: str
	real_name: str
	foo: str


@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_document_cls(client_with_index):
	await client_with_index.add_document('auser', *dict(username='auser', real_name='A User', foo='bar').items())
	doc = await client_with_index.get_document('auser', document_cls=User)
	assert isinstance(doc, User)
