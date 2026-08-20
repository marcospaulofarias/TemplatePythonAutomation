import pytest

from resources.UiAutomationClass import UiAutomationClass


class FakeElement:
    def __init__(self, control_type="ButtonControl"):
        self.ControlTypeName = control_type


class FakePrint:
    def __init__(self):
        self.calls = 0

    def print_error(self, element_to_print=None):
        self.calls += 1


def make_ui(behavior):
    """Instancia UiAutomationClass SEM passar pelo __init__ pesado
    (que dispara PrintAutomation -> PathManager -> leitura do .env).
    Monta só o mínimo que interact_element usa: get_interactions e printautomation.

    Importante: interact_element chama self.get_interactions(interaction_type=...)
    e não lê self.interactions diretamente, então o mock precisa substituir o
    método, não um atributo de dicionário estático.
    """
    ui = object.__new__(UiAutomationClass)
    ui.get_interactions = lambda interaction_type='sendkeys': {"ButtonControl": behavior}
    ui.printautomation = FakePrint()
    return ui


def test_sucesso_imediato_retorna_true_em_1_chamada():
    calls = {"n": 0}

    def ok(el, value=None):
        calls["n"] += 1
        return True

    ui = make_ui(ok)
    assert ui.interact_element(FakeElement(), max_interact_seconds=1, interval=0.01) is True
    assert calls["n"] == 1


def test_retorno_none_e_tratado_como_sucesso():
    """SendKeys retorna None; None não é False, então conta como sucesso."""
    calls = {"n": 0}

    def none_ret(el, value=None):
        calls["n"] += 1
        return None

    ui = make_ui(none_ret)
    assert ui.interact_element(FakeElement(), max_interact_seconds=1, interval=0.01) is True
    assert calls["n"] == 1


def test_false_faz_retry_ate_dar_certo():
    calls = {"n": 0}

    def false_then_ok(el, value=None):
        calls["n"] += 1
        return calls["n"] > 2  # False, False, True

    ui = make_ui(false_then_ok)
    assert ui.interact_element(FakeElement(), max_interact_seconds=1, interval=0.01) is True
    assert calls["n"] == 3


def test_excecao_faz_retry_ate_dar_certo():
    calls = {"n": 0}

    def raise_then_ok(el, value=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("boom")
        return True

    ui = make_ui(raise_then_ok)
    assert ui.interact_element(FakeElement(), max_interact_seconds=1, interval=0.01) is True
    assert calls["n"] == 2


def test_sempre_false_retorna_false_e_tira_print():
    ui = make_ui(lambda el, value=None: False)
    with pytest.raises(RuntimeError):
        ui.interact_element(FakeElement(), max_interact_seconds=0.2, interval=0.05)
    assert ui.printautomation.calls == 1


def test_tipo_sem_interacao_levanta_valueerror_e_printa():
    """Quando não há interação mapeada para o ControlTypeName, o método
    real levanta ValueError (não retorna False) e chama print_error antes."""
    ui = make_ui(lambda el, value=None: True)
    with pytest.raises(ValueError):
        ui.interact_element(FakeElement(control_type="TextControl"))
    assert ui.printautomation.calls == 1