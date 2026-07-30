import pytest

from resources.UiAutomationClass import UiAutomationClass

# _verify_dict_params não usa `self`, então dá para chamá-lo sem instanciar a classe.
# Isso evita a cadeia de construção (PrintAutomation -> PathManager -> leitura do .env
# e criação de diretórios) só para testar uma função de validação pura.
verify = UiAutomationClass._verify_dict_params


@pytest.mark.parametrize("params, esperado", [
    ({"name": "X"}, True),                       # 1 valor preenchido -> válido
    ({"name": "X", "classname": None}, True),    # ao menos 1 preenchido -> válido
    ({"name": None, "classname": "X"}, True),    # ordem não importa
    ({"name": None}, False),                     # todos None -> inválido
    ({}, False),                                 # vazio -> inválido
])
def test_verify_dict_params(params, esperado):
    assert verify(None, params) is esperado
