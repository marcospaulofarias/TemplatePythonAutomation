import time
from loguru import logger
import uiautomation as auto
from resources.PrintAutomation import PrintAutomation

class UiAutomationClass:
    """Classe para automação de interface gráfica RPA usando uiautomation.

    :param process_id: Identificador do processo para logs e rastreamento.
    :param process_type: Tipo do processo para logs e rastreamento.
    :param process_machine: Nome da máquina para logs e rastreamento.
    :returns None:
    """
    def __init__(self, process_id: str, process_type: str, process_machine: str) -> None:
        self.printautomation = PrintAutomation(process_id=process_id,
                                               process_type=process_type,
                                               process_machine=process_machine)
                                               
        self.controls = {
            "Button": auto.ButtonControl,
            "Edit": auto.EditControl,
            "EditText": auto.TextControl,
            "Window": auto.WindowControl
        }

        self.interactions = {
            "EditControl": lambda element, value=None: element.SendKeys(value),
            "TextControl": lambda element, value=None: element.SendKeys(value),
            "ButtonControl": lambda element, value=None: element.GetInvokePattern().Invoke(),
        }

    def find_element(self, element_type: str, params: dict, screen: auto.WindowControl = None) -> auto.Control|ValueError:
        """Captura um elemento usando os parâmetros fornecidos.

        :param element_type: tipo do elemento a ser buscado (ex: 'Button', 'Edit', 'Window').
        :param params: dicionário de parâmetros para a busca do elemento.
            Exemplos: automationid, classname, name, depth, type.
        :param screen: elemento de tela a partir do qual a busca deve ser realizada.
        :returns: o controle encontrado.
        :raises ValueError: se não encontrar o elemento.
        """
        if not self._verify_dict_params(dict_params=params):
            raise ValueError("É necessário passar no mínimo parâmetro")
        return self._try_element(element_type=element_type, params=params, screen=screen)

    def interact_element(self, element: auto.Control, value: str = None,
                         max_interact_seconds: float = 20, interval: float = 1.0) -> bool|RuntimeError:
        """Tenta interagir com o elemento até atingir o timeout.

        :param element: elemento a ser interagido (uiautomation.Control).
        :param value: valor a ser enviado (para EditControl/TextControl).
        :param max_interact_seconds: tempo máximo (s) para tentar interagir com o elemento.
        :param interval: intervalo (s) entre as tentativas de interação.
        :returns True: se a interação for bem-sucedida.
        :raises RuntimeError: se ocorrer qualquer falha.
        """
        method_element = self.interactions.get(element.ControlTypeName)
        if not method_element:
            self.printautomation.print_error()
            raise ValueError(f"Nenhuma interação definida para o tipo: {element.ControlTypeName}")

        deadline = time.monotonic() + max_interact_seconds
        last_error = None
        while time.monotonic() < deadline:
            try:
                result = method_element(element, value)
                if result is False:
                    raise RuntimeError("A interação retornou False")
                return True
            except Exception as error_x:
                last_error = error_x
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))
        self.printautomation.print_error(element_to_print=element)
        logger.critical(f"Não foi possível interagir com o elemento após {max_interact_seconds}s: {last_error}")
        raise RuntimeError(f"Não foi possível interagir com o elemento após {max_interact_seconds}s: {last_error}") from last_error

    def _verify_dict_params(self, dict_params) -> bool:
        """Verifica se foi passado ao menos um parâmetro válido.

        :param dict_params: dicionário de parâmetros a ser verificado.
        :returns True: se existir ao menos um par chave/valor não nulo.
        :returns False: se todos valores forem nulos.
        """
        if all(k is None or v is None for k, v in dict_params.items()):
            return False
        return True
    
    def _try_element(self, element_type: str, params: dict, max_search_seconds: float = 20, search_interval: float = 1.0, screen: auto.WindowControl = None) -> auto.Control|ValueError|LookupError:
        """Busca um elemento repetidamente até encontrá-lo ou estourar o timeout.

        :param element_type: tipo do elemento a ser buscado (ex: 'Button', 'Edit', 'Window').
        :param params: dicionário de parâmetros para a busca do elemento.
        :param screen: elemento de tela a partir do qual a busca deve ser realizada.
        :param max_search_seconds: tempo máximo (s) para tentar encontrar o elemento.
        :param search_interval: intervalo (s) entre as tentativas de busca.
        :returns: o controle encontrado.
        :raises ValueError: se o tipo do elemento não for informado.
        :raises LookupError: se o elemento não for encontrado.
        """
        if not element_type or element_type not in self.controls:
            raise ValueError("Obrigatório informar o tipo do elemento")
        control_cls = self.controls.get(element_type)
        element = control_cls(searchFromControl=screen,
                              ClassName=params.get("classname"),
                              Name=params.get("name"),
                              AutomationId=params.get("automationid"),
                              Depth=params.get("depth"))
        try:
            if element.Exists(maxSearchSeconds=max_search_seconds, searchIntervalSeconds=search_interval):
                if element_type == "Window":
                    element.SetActive()
                    element.SetFocus()
                elif screen:
                    screen.SetActive()
                    screen.SetFocus()
                return element
            raise LookupError(f"{element_type} não encontrado: {params}")
        except Exception as error_x:
            self.printautomation.print_error(element_to_print=screen)
            logger.critical(f"Erro ao buscar {element_type}: {error_x}")
            raise LookupError(f"Erro ao buscar {element_type}: {error_x}") from error_x
