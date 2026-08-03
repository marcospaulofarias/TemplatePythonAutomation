from time import sleep
from loguru import logger
from resources.Browser import Browser

class BancoCentral(Browser):
    def __init__(self, process_id: str, process_type: str, process_machine: str, headless: bool=False) -> None:
        """Classe para interagir com o site do Banco Central buscando cotações das moedas.
        
        :param process_id: Id do processo.
        :param process_type: Tipo do processo.
        :param process_machine: Máquina que está executando o processo.
        :param headless: Headless verdadeiro = Não abre o navegador usando UI; Headless falso = Abre o navegador usando UI.
        """
        super().__init__(process_id=process_id, process_type=process_type, process_machine=process_machine, headless=headless)
        logger.debug(f"BancoCentral.__init__: process_id={process_id} process_type={process_type} process_machine={process_machine} headless={headless}")

    def get_dolar(self) -> str:
        logger.debug("BancoCentral.get_dolar: iniciando busca da cotação do dólar")
        """Função para buscar especificamente a cotação do dólar.
        
        :return: str(cotacao_dolar).
        """
        sleep(10)
        cotacao = self.element_response(
            method=self.by_methods["tag_name"],
            element_id="cotacao",
            message_success="Tag <cotacao> capturada com sucesso",
            message_error="Erro ao capturar a tag <cotacao>"
        )

        tables = self.elements_response(
            method=self.by_methods["css_selector"],
            element_id=".table.light",
            message_success="Tabela .table.light capturada com sucesso",
            message_error="Erro ao capturar a tabela .table.light",
            element=cotacao
        )

        spans = self.elements_response(
            method=self.by_methods["tag_name"],
            element_id="span",
            message_success="Spans capturados com sucesso",
            message_error="Erro ao capturar os spans",
            element=tables[0]
        )

        if len(spans) < 2:
            logger.error("BancoCentral.get_dolar: não há spans suficientes dentro da tabela")
            raise RuntimeError("Não há spans suficientes dentro da tabela")

        result = spans[1].text
        logger.debug(f"BancoCentral.get_dolar: resultado={result}")
        return result

    def _open_converter_menu(self) -> None:
        logger.debug("BancoCentral._open_converter_menu: abrindo menu de conversão")
        """Função para abrir o conversor de moedas no site do Banco Central.
        
        :return: None.
        """
        self.element_response(
            method=self.BY_METHODS["id"],
            element_id="button-converter-para",
            message_success="Menu de conversão aberto",
            message_error="Não foi possível abrir o menu de conversão",
            click=True
        )

    def _get_coin_options(self):
        logger.debug("BancoCentral._get_coin_options: capturando opções de moeda")
        """Função para capturar as moedas disponíveis para verificar a cotação.
        
        :return: list(nomes_de_moedas_cotacao).
        """
        return self.elements_response(
            method=self.by_methods["css_selector"],
            element_id="#moedaResultado1 a.dropdown-item",
            message_success="Opções de moedas capturadas com sucesso",
            message_error="Erro ao capturar as opções de moedas"
        )

    def get_all_coins(self) -> list:
        """Função para capturar as moedas disponíveis para verificar a cotação.
        
        :return: list(nomes_de_moedas_cotacao).
        """
        logger.debug("BancoCentral.get_all_coins: iniciando captura de todas as moedas")
        self.get_site(url_site='https://www.bcb.gov.br/conversao/', try_repetitons=5, time_new_retry=1)
        self._open_converter_menu()
        coin_options = self._get_coin_options()
        coins = []
        for coin in coin_options:
            inner = coin.get_attribute("innerHTML") or coin.text
            coin_name = inner.strip()
            coins.append({
                "name": coin_name,
                "element": coin
            })
        self._open_converter_menu()
        logger.debug(f"BancoCentral.get_all_coins: capturou {len(coins)} moedas")
        return coins

    def get_all_coins_values(self) -> dict:
        logger.debug("BancoCentral.get_all_coins_values: iniciando cálculo das cotações de todas as moedas")
        dict_coins = {}
        coins = self.get_all_coins()
        last_conversao = ''
        line = 1
        first_time = True
        for coin in coins:
            conversion = self.select_coin_by_inner_html(last_result=last_conversao, coin_html=coin["name"])
            if first_time:
                sleep(6)
            conversion_value = conversion.split(" ")[-3]
            dict_coins[coin["name"]] = conversion_value
            last_conversao = conversion
            line += 1
            first_time = False
        return dict_coins

    def select_coin_by_inner_html(self, last_result: str, coin_html: str):
        logger.debug(f"BancoCentral.select_coin_by_inner_html: last_result={last_result} coin_html={coin_html}")
        """Função para selecionar uma moeda para cotação.
        
        :param last_result: Último resultado obtido com a função para poder verificar se foi carregado corretamente o valor.
        :param coin_html: Moeda para cotação a ser selecionada.
        :return: str(result).
        """
        self._open_converter_menu()
        coin_options = self._get_coin_options()
        for coin in coin_options:
            inner = (coin.get_attribute("innerHTML") or coin.text).strip()
            logger.debug(f"BancoCentral.select_coin_by_inner_html: testando moeda inner={inner}")
            if coin_html in inner:
                coin.click()
                result = self._get_result_convertion(last_result=last_result)
                if result:
                    logger.debug(f"BancoCentral.select_coin_by_inner_html: selecionou moeda {coin_html} result={result}")
                    return result
        raise RuntimeError(f"Moeda não encontrada com base em innerHTML: {coin_html}")

    def _get_result_convertion(self, last_result: str, num_repetitions: int = 10) -> str:
        logger.debug(f"BancoCentral._get_result_convertion: last_result={last_result} num_repetitions={num_repetitions}")
        """FUnção para buscar o resultado de uma cotação.
        
        :param last_result: Último resultado obtido com a função para poder verificar se foi carregado corretamente o valor.
        :param num_retitions: Quantidade de tentativas para buscar o resultado verificando se foi carregado corretamente.
        :return: str(resultado) se chegar no limite, significa que a cotação da moeda buscada é igual a moeda anterior.
        """
        for repetition in range(num_repetitions):
            logger.debug(f"BancoCentral._get_result_convertion: tentativa {repetition + 1}")
            resultado = self.elements_response(method=self.BY_METHODS["class_name"], 
                                                            element_id="col-12", 
                                                            message_success="ok", 
                                                            message_error="erro")
            value_result = resultado[1].text.split(" = ")[1].split(" ")[0]
            if last_result != '':
                value_last_result = last_result.split(" = ")[1].split(" ")[0]
            else:
                value_last_result = 'diferente'
            if last_result != resultado[1].text and value_last_result != value_result:
                return resultado[1].text
            sleep(1)
        return resultado[1].text

if __name__ == '__main__':
    bancocentral = BancoCentral(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    coins_values = bancocentral.get_all_coins_values()
    logger.debug(f'COINS_VALUES: {coins_values}')
