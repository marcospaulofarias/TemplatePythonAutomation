import time
from _ctypes import COMError
from loguru import logger
import uiautomation as auto
from resources.PrintAutomation import PrintAutomation
from resources.logger_config import configure_logger

class UiAutomationClass:
    """Classe para automação de interface gráfica RPA usando uiautomation.

    O logger global é configurado para gravar em arquivo de log local quando
    `process_id`, `process_type` e `process_machine` são informados.
    O arquivo de log padrão é gerado em `./logs/<process_id>_<process_type>_<process_machine>.log`.

    :param process_id: Identificador do processo para logs e rastreamento.
    :param process_type: Tipo do processo para logs e rastreamento.
    :param process_machine: Nome da máquina para logs e rastreamento.
    :returns: None
    """
    def __init__(self, process_id: str, process_type: str, process_machine: str) -> None:
        configure_logger(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.printautomation = PrintAutomation(process_id=process_id,
                                               process_type=process_type,
                                               process_machine=process_machine)
                                               
        self.controls = {
            "Button": auto.ButtonControl,
            "Edit": auto.EditControl,
            "EditText": auto.TextControl,
            "Window": auto.WindowControl,
            "Panel": auto.PaneControl,
            "ComboBox": auto.ComboBoxControl,
            "RadioButton": auto.RadioButtonControl,
            "MenuItem": auto.MenuItemControl,
            "CheckBox": auto.CheckBoxControl,
        }

    def get_interactions(self, interaction_type: str = "sendkeys") -> dict:
        """Retorna o mapa de interações para o tipo escolhido.

        :param interaction_type: 'sendkeys' simula o teclado e dispara os eventos do app;
            'setvalue' escreve direto via ValuePattern, sem simular teclas.
        :returns: dicionário {ControlTypeName: função de interação}.
        :raises ValueError: se o tipo de interação não for suportado.
        """
        logger.debug(f"get_interactions: interaction_type={interaction_type}")
        match interaction_type:
            case "sendkeys":
                interactions = {
                    "EditControl": lambda element, value=None: element.SendKeys(value),
                    "TextControl": lambda element, value=None: element.SendKeys(value),
                    "ButtonControl": lambda element, value=None: element.GetInvokePattern().Invoke(),
                    "RadioButtonControl": lambda element, value=None: element.GetLegacyIAccessiblePattern().DoDefaultAction(),
                    "MenuItemControl": lambda element, value=None: element.GetInvokePattern().DoDefaultAction(),
                    "CheckBoxControl": lambda element, value=None: element.GetTogglePattern().DoDefaultAction(),
                }
            case "setvalue":
                interactions = {
                    "EditControl": lambda element, value=None: element.GetValuePattern().SetValue(value),
                    "TextControl": lambda element, value=None: element.GetValuePattern().SetValue(value),
                    "ButtonControl": lambda element, value=None: element.GetInvokePattern().Invoke(),
                    "RadioButtonControl": lambda element, value=None: element.GetLegacyIAccessiblePattern().DoDefaultAction(),
                    "MenuItemControl": lambda element, value=None: element.GetInvokePattern().DoDefaultAction(),
                    "CheckBoxControl": lambda element, value=None: element.GetTogglePattern().DoDefaultAction(),
                }
            case _:
                raise ValueError(f"Interação inválida: '{interaction_type}'. Use 'sendkeys' ou 'setvalue'")
        logger.debug(f"interactions map criado para {interaction_type}")
        return interactions

    def find_element(self, element_type: str, 
                     params: dict, 
                     screen: auto.WindowControl = None, 
                     max_search_seconds: float = 30, raise_on_error: bool = True) -> auto.Control:
        """Captura um elemento usando os parâmetros fornecidos.

        :param element_type: tipo do elemento a ser buscado (ex: 'Button', 'Edit', 'Window').
        :param params: dicionário de parâmetros para a busca do elemento.
            Exemplos: automationid, classname, name, depth, type.
        :param screen: elemento de tela a partir do qual a busca deve ser realizada.
        :returns: o controle encontrado.
        :raises ValueError: se não encontrar o elemento.
        """
        logger.debug(f"find_element: element_type={element_type} params={params} screen={screen} max_search_seconds={max_search_seconds}")
        if not self._verify_dict_params(dict_params=params):
            logger.debug("find_element: parâmetros inválidos ou todos nulos")
            raise ValueError("É necessário passar no mínimo parâmetro")
        element = self._try_element(element_type=element_type, 
                                 params=params, screen=screen, 
                                 max_search_seconds=max_search_seconds, raise_on_error=raise_on_error)
        logger.debug(f"find_element: elemento retornado para {element_type} {params}")
        return element

    def interact_element(self, element: auto.Control, 
                         value: str = None,
                         max_interact_seconds: float = 20, 
                         interval: float = 1.0, 
                         interaction_type: str = 'sendkeys') -> bool:
        """Tenta interagir com o elemento até atingir o timeout.

        :param element: elemento a ser interagido (uiautomation.Control).
        :param value: valor a ser enviado (para EditControl/TextControl).
        :param max_interact_seconds: tempo máximo (s) para tentar interagir com o elemento.
        :param interval: intervalo (s) entre as tentativas de interação.
        :param interaction_type: forma de interagir com o elemento ('sendkeys' ou 'setvalue'),
            conforme get_interactions.
        :returns True: se a interação for bem-sucedida.
        :raises RuntimeError: se ocorrer qualquer falha.
        """
        logger.debug(f"interact_element: ControlTypeName={element.ControlTypeName} value={value} interaction_type={interaction_type} max_interact_seconds={max_interact_seconds} interval={interval}")
        interactions = self.get_interactions(interaction_type=interaction_type)
        method_element = interactions.get(element.ControlTypeName)
        if not method_element:
            self.printautomation.print_error()
            logger.debug(f"interact_element: interação não definida para {element.ControlTypeName}")
            raise ValueError(f"Nenhuma interação definida para o tipo: {element.ControlTypeName}")

        deadline = time.monotonic() + max_interact_seconds
        last_error = None
        while time.monotonic() < deadline:
            try:
                result = method_element(element, value)
                if result is False:
                    raise RuntimeError("A interação retornou False")
                logger.debug(f"interact_element: interação bem-sucedida para {element.ControlTypeName}")
                return True
            except Exception as error_x:
                last_error = error_x
                logger.warning(f"interact_element: tentativa falhou para {element.ControlTypeName}: {error_x}")
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
    
    def _try_element(self, element_type: str, params: dict, max_search_seconds: float = 20, search_interval: float = 1.0, screen: auto.WindowControl = None, raise_on_error: bool = True) -> auto.Control:
        """Busca um elemento repetidamente até encontrá-lo ou estourar o timeout.

        :param element_type: tipo do elemento a ser buscado (ex: 'Button', 'Edit', 'Window').
        :param params: dicionário de parâmetros para a busca do elemento.
        :param screen: elemento de tela a partir do qual a busca deve ser realizada.
        :param max_search_seconds: tempo máximo (s) para tentar encontrar o elemento.
        :param search_interval: intervalo (s) entre as tentativas de busca.
        :returns: o controle encontrado.
        :raises ValueError: se o tipo do elemento não for informado.
        :raises LookupError: se o elemento não for encontrado dentro do timeout.
        """
        if not element_type or element_type not in self.controls:
            raise ValueError("Obrigatório informar o tipo do elemento")
        control_cls = self.controls.get(element_type)
        element = control_cls(searchFromControl=screen,
                              ClassName=params.get("classname"),
                              Name=params.get("name"),
                              AutomationId=params.get("automationid"),
                              Depth=params.get("depth"))
        deadline = time.monotonic() + max_search_seconds
        last_error = None
        while time.monotonic() < deadline:
            try:
                # Exists é chamado em fatias curtas porque ele não protege o FindControl
                # interno: um COMError do provider aborta a busca inteira em vez de repetir.
                if element.Exists(maxSearchSeconds=search_interval, searchIntervalSeconds=search_interval):
                    if element_type == "Window":
                        element.SetActive()
                        element.SetFocus()
                    elif screen:
                        screen.SetActive()
                        screen.SetFocus()
                    logger.debug(f"{element_type} encontrado: {params}")
                    return element
            except COMError as error_x:
                # O provider UIA do app falha se a árvore mudar durante a varredura
                # (janela sendo redesenhada). É transitório: vale tentar de novo.
                last_error = error_x
                logger.warning(f"Provider UIA falhou ao buscar {element_type}, tentando novamente: {error_x}")
                time.sleep(search_interval)
            except Exception as error_x:
                self.printautomation.print_error(element_to_print=screen)
                logger.critical(f"Erro ao buscar {element_type}: {error_x}")
                if raise_on_error:
                    raise LookupError(f"Erro ao buscar {element_type}: {error_x}") from error_x
                return None

        self.printautomation.print_error(element_to_print=screen)
        logger.critical(f"{element_type} não encontrado: {params} | último erro: {last_error}")
        raise LookupError(f"{element_type} não encontrado: {params} | último erro: {last_error}")

    def get_elements_root(self, element_type: str = None, process_id: int = None) -> list[auto.Control]:
        """Lista os elementos de topo (telas) a partir do Desktop.

        Útil para mapear quais janelas estão abertas antes de automatizá-las.

        :param element_type: filtra por tipo conforme self.controls (ex: 'Window'). None traz todos.
        :param process_id: filtra pelo PID dono da janela (ex: o PID do contabil.exe). None traz todos.
        :returns: lista dos controles de topo encontrados.
        :raises ValueError: se element_type for informado e não existir em self.controls.
        """
        logger.debug(f"get_elements_root: element_type={element_type} process_id={process_id}")
        if element_type and element_type not in self.controls:
            raise ValueError(f"Tipo inválido: {element_type}. Use um de {list(self.controls)}")
        expected_type = self.controls[element_type].__name__ if element_type else None

        elements_root = []
        for element in auto.GetRootControl().GetChildren():
            try:
                if expected_type and element.ControlTypeName != expected_type:
                    continue
                if process_id and element.ProcessId != process_id:
                    continue
                logger.debug(f'{element.ControlTypeName} | {element.ClassName} | PID {element.ProcessId} | {element.Name!r}')
                elements_root.append(element)
            except Exception as error_x:
                logger.warning(f'Não foi possível ler um controle de topo: {error_x}')
        logger.debug(f"get_elements_root: retornando {len(elements_root)} elementos")
        return elements_root
