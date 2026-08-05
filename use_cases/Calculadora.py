from loguru import logger
from resources.UiAutomationClass import UiAutomationClass

class Calculadora(UiAutomationClass):
    """Automação da calculadora do Windows usando uiautomation."""

    def __init__(self, process_id: str, process_type: str, process_machine: str):
        super().__init__(process_id=process_id, 
                         process_type=process_type, 
                         process_machine=process_machine)
        logger.debug(f"Calculadora.__init__: process_id={process_id} process_type={process_type} process_machine={process_machine}")


    def multiply_coin_value(self, coin_value: str, multiply_value: str) -> str:
        logger.debug(f"Calculadora.multiply_coin_value: coin_value={coin_value} multiply_value={multiply_value}")
        """Multiplica um valor pela cotação da moeda exibida na calculadora.

        :param multiply_value: Valor a ser multiplicado pelo dólar.
        :param coin_value: Cotação do dólar a ser usada na operação.
        :return: Texto exibido no resultado da calculadora após a operação.
        """
        self.window_calculadora = self.find_element(element_type="Window", params={"name": "Calculadora"})
        text_field = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "NormalOutput"})
        self.interact_element(text_field, value=coin_value.replace(".", ","))
        button_multiply = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Multiplicar por"})
        self.interact_element(button_multiply)
        result_field = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "CalculatorResults"})
        self.interact_element(result_field, value=str(multiply_value).replace(".", ","))
        equal_to = self.find_element(screen=self.window_calculadora, element_type="Button", params={"name": "Igual a"})
        self.interact_element(equal_to)
        result_text = self.find_element(screen=self.window_calculadora, element_type="EditText", params={"automationid": "CalculatorResults"})
        return result_text.Name
