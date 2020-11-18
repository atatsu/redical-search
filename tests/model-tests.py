from datetime import datetime, timezone
from typing import Optional

from redicalsearch import Document


def test_hset_optionals_stripped():
	class MyDoc(Document):
		attr1: str
		attr2: str
		attr3: Optional[str]
		attr4: Optional[str]

	doc = MyDoc(id='an-id', attr1='a', attr2='b', attr4='c')
	actual = doc.hset()
	expected = dict(attr1='a', attr2='b', attr4='c')
	assert expected == actual


def test_hset_bool_to_int():
	class MyDoc(Document):
		attr1: bool
		attr2: bool

	doc = MyDoc(id='an-id', attr1=True, attr2=False)
	actual = doc.hset()
	assert 1 == actual['attr1'] and actual['attr1'] is not True
	assert 0 == actual['attr2'] and actual['attr2'] is not False


def test_hset_datetime_to_timestamp():
	class MyDoc(Document):
		attr1: datetime

	dt = datetime.now(timezone.utc)
	doc = MyDoc(id='an-id', attr1=dt)
	actual = doc.hset()
	expected = dict(attr1=int(dt.timestamp() * 1000))
	assert expected == actual
