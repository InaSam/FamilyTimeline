import pytest
from timeline import Person
from timeline import get_marriage
from timeline import get_start_date_b
from timeline import get_start_date_w


def test_get_marriage():
    husband = Person.get("01000100011")
    wife = Person.get("01000200010")
    assert get_marriage(husband, wife) == {"ends": 0, "starts": "1934"}

    husband = None
    wife = Person.get("01000200010")
    assert get_marriage(husband, wife) == None

    husband = Person.get("01000100011")
    wife = Person.get("01000700010")
    assert get_marriage(husband, wife) == {"ends": 0, "starts": 0}


def test_get_start_date_b():
    assert get_start_date_b(1939, 1900, 1899) == 1890
    assert get_start_date_b(1939, 1895, 1900) == 1890
    assert get_start_date_b(1934, 1898, None) == 1890
    assert get_start_date_b(1939, None, 1905) == 1900
    assert get_start_date_b(1939, None, None) == 1880


def test_get_start_date_w():
    assert get_start_date_w(1945, None) == 1940
    assert get_start_date_w(None, 1956) == 1850
    with pytest.raises(SystemExit) as sample:
        get_start_date_w(None, None)
    assert sample.type == SystemExit

