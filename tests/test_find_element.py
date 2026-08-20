import pytest

from resources.UiAutomationClass import UiAutomationClass


class FakePrint:
    def __init__(self):
        self.calls = 0

    def print_error(self, element_to_print=None):
        self.calls += 1


class FakeControl:
    def __init__(self, exists_result, **kwargs):
        self._exists_result = exists_result
        self.kwargs = kwargs

    def Exists(self, maxSearchSeconds=0, searchIntervalSeconds=0):
        if isinstance(self._exists_result, Exception):
            raise self._exists_result
        return self._exists_result


def control_class(exists_result):
    """Simula auto.ButtonControl etc.: chamada com os kwargs de busca, devolve
    um FakeControl cujo .Exists() retorna exists_result (ou levanta, se exceção)."""
    def factory(**kwargs):
        return FakeControl(exists_result, **kwargs)

    return factory


def make_ui(controls):
    ui = object.__new__(UiAutomationClass)
    ui.controls = controls
    ui.printautomation = FakePrint()
    return ui


def test_retorna_o_controle_quando_existe():
    ui = make_ui({"Button": control_class(True)})
    element = ui.find_element(element_type="Button", params={"name": "OK"})
    assert isinstance(element, FakeControl)
    assert element.kwargs["Name"] == "OK"       # o param "name" virou kwarg "Name"
    assert ui.printautomation.calls == 0         # sucesso não printa


def test_lanca_lookuperror_quando_nao_existe():
    ui = make_ui({"Button": control_class(False)})
    with pytest.raises(LookupError, match="Button"):
        ui.find_element(element_type="Button", params={"name": "Fantasma"})
    assert ui.printautomation.calls == 1         # falha tira print

def test_repassa_screen_como_search_from_control():
    """Buscar dentro de uma janela já encontrada: o screen precisa chegar ao
    controle como searchFromControl (guarda contra a regressão do 'screen.self')."""
    ui = make_ui({"Button": control_class(True)})
    janela = object()  # sentinela representando a WindowControl já encontrada
    element = ui.find_element(element_type="Button", params={"name": "Um"}, screen=janela)
    assert element.kwargs["searchFromControl"] is janela


def test_sem_screen_search_from_control_e_none():
    ui = make_ui({"Button": control_class(True)})
    element = ui.find_element(element_type="Button", params={"name": "Um"})
    assert element.kwargs["searchFromControl"] is None


def test_lanca_valueerror_para_tipo_desconhecido():
    ui = make_ui({"Button": control_class(True)})
    with pytest.raises(ValueError):
        ui.find_element(element_type="Slider", params={"name": "OK"})


def test_lanca_valueerror_para_params_invalidos():
    ui = make_ui({"Button": control_class(True)})
    with pytest.raises(ValueError):
        ui.find_element(element_type="Button", params={"name": None})
