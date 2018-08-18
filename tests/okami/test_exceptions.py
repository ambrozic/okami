from okami.exceptions import OkamiException


def test_okami_exception():
    assert OkamiException().msg == ""
    assert OkamiException().extra is None
    assert OkamiException(msg="abc").msg == "abc"
    assert OkamiException(msg="abc").extra is None
    assert OkamiException(msg="abc", extra=dict(a=1)).msg == "abc"
    assert OkamiException(msg="abc", extra=dict(a=1)).extra == dict(a=1)
