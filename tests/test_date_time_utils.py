from datetime import datetime

from utils.date_time_utils import get_numeric_timestamp


def test_retorna_somente_digitos():
    assert get_numeric_timestamp().isdigit()


def test_retorna_string_nao_vazia():
    result = get_numeric_timestamp()
    assert isinstance(result, str)
    assert len(result) > 0


def test_saida_deterministica_com_datetime_fixo(monkeypatch):
    """Com um datetime fixo, a saída é exatamente os dígitos daquele instante."""
    fixo = datetime(2026, 7, 10, 17, 30, 45, 123456)

    class FakeDateTime:
        @classmethod
        def now(cls):
            return fixo

    monkeypatch.setattr("utils.date_time_utils.datetime", FakeDateTime)
    assert get_numeric_timestamp() == "20260710173045123456"
