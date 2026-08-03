from resources.Initializator import Initializator
from resources.SerialKiller import SerialKiller
from resources.Txt import Txt
from resources.Xlsx import Xlsx
from resources.Outlook import Outlook
from use_cases.BancoCentral import BancoCentral
from use_cases.Calculadora import Calculadora
from time import sleep
from resources.logger_config import configure_logger
from loguru import logger

class AutomationCoins:
    def __init__(self, process_id: str, process_type: str, process_machine: str, necessary_apps: list[str]) -> None:
        configure_logger(process_id=process_id, process_type=process_type, process_machine=process_machine)
        logger.debug(f"AutomationCoins.__init__: process_id={process_id} process_type={process_type} process_machine={process_machine} necessary_apps={necessary_apps}")
        self.necessary_apps = necessary_apps
        self.initializator = Initializator(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.serialkiller = SerialKiller(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.txt = Txt(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.xlsx = Xlsx(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.outlook = Outlook()
        self.bancocentral = BancoCentral(process_id=process_id, process_type=process_type, process_machine=process_machine, headless=True)
        self.calculadora = Calculadora(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def finalize_apps(self) -> None:
        logger.debug(f"AutomationCoins.finalize_apps: necessary_apps={self.necessary_apps}")
        self.serialkiller.kill_program_by_name(programs_to_kill=self.necessary_apps)
        self.serialkiller.kill_program_by_name(programs_to_kill=['msedge'])  # Finaliza o browser caso esteja aberto
        self.bancocentral.driver = None

    def initialize_apps(self) -> None:
        logger.debug("AutomationCoins.initialize_apps: iniciando aplicativos necessários")
        self.initializator.run_program(programs_to_execute=['calculadora'])
        # Para o browser é recomendado abrir apenas pelo selenium ao invés de .exe como no Initializator.
        self.bancocentral._open_browser()

    def _get_all_bc_coins(self) -> list:
        logger.debug("AutomationCoins._get_all_bc_coins: solicitando cotações do Banco Central")
        return self.bancocentral.get_all_coins_values()

    def _multiply_using_calculator(self, value_to_divide: float, value_multiply_by: float) -> str:
        logger.debug(f"AutomationCoins._multiply_using_calculator: value_to_divide={value_to_divide} value_multiply_by={value_multiply_by}")
        return self.calculadora.multiply_coin_value(coin_value=value_to_divide, multiply_value=value_multiply_by)

    def _add_coin_to_txt(self, txt_file:str, result_coin: list[str]) -> None:
        self.txt.new_or_overwrite_txt(txt_file=txt_file, data_to_overwrite=result_coin, create_txt=True)

    def _add_coin_to_xlsx(self, xlsx_file: str, sheet_name: str, cell_reference: str, result_coin: str) -> None:
        self.xlsx.set_cell_value(xlsx_file=xlsx_file, sheet_name=sheet_name, cell_reference=cell_reference, value=result_coin, create_sheet=True, create_xlsx=True)
        self.xlsx.save_workbook(xlsx_file=xlsx_file)

    def _send_email(self, send_to: list[str], files_to_send: list[str]) -> None:
        self.outlook.send_email(
            recipients=send_to, 
            subject='Cotação das moedas hoje', 
            body='Olá\nSeguem anexos arquivos txt e xlsx referentes a cotação das moedas no dia de hoje.', 
            attachments=files_to_send
        )
        
    def manage_coins(self, send_to: list[str], multiply_value: float, files_to_send: list[str]) -> None:
        coins = self._get_all_bc_coins()
        logger.debug(f"AutomationCoins.manage_coins: coins={coins}")
        coins_txt = [f'{coin};{coin_value};' for coin, coin_value in coins.items()]
        self._add_coin_to_txt(txt_file=files_to_send[0], result_coin=[])
        self._add_coin_to_txt(txt_file=files_to_send[0], result_coin=coins_txt)
        line = 1
        for coin, value in coins.items():
            logger.debug(f"AutomationCoins.manage_coins: processando moeda={coin} valor={value} linha={line}")
            result_multiply = self.calculadora.multiply_coin_value(coin_value=value, multiply_value=multiply_value)
            self._add_coin_to_xlsx(xlsx_file=files_to_send[1], sheet_name='CotacaoMoedas', cell_reference=f'A{line}', result_coin=coin)
            self._add_coin_to_xlsx(xlsx_file=files_to_send[1], sheet_name='CotacaoMoedas', cell_reference=f'B{line}', result_coin=value)
            self._add_coin_to_xlsx(xlsx_file=files_to_send[1], sheet_name='CotacaoMoedas', cell_reference=f'C{line}', result_coin=result_multiply)
            line += 1
        self._send_email(send_to=send_to, files_to_send=files_to_send)

    def run(self, multiply_value: float, files_to_send: list[str], try_attempts: int, time_to_retry: float = 1) -> None:
        logger.debug(f"AutomationCoins.run: files_to_send={files_to_send} multiply_value={multiply_value} try_attempts={try_attempts} time_to_retry={time_to_retry}")
        users = self.get_users()
        users_ready = self.txt.read_txt(txt_file='.\\workbooks\\users_ready.txt')
        logger.debug(f"AutomationCoins.run: users={users} users_ready={users_ready}")
        if not users_ready:
            self.txt.new_or_overwrite_txt(txt_file='.\\workbooks\\users_ready.txt', data_to_overwrite=[], create_txt=True)
            users_ready = self.txt.read_txt(txt_file='.\\workbooks\\users_ready.txt')
        if users:
            for user in users:
                if user not in users_ready:
                    for attempt in range(try_attempts):
                        try:
                            self.finalize_apps()
                            self.initialize_apps()
                            self.manage_coins(send_to=[user], multiply_value=multiply_value, files_to_send=files_to_send)
                            self.finalize_apps()
                            self.txt.add_line_to_txt(txt_file='.\\workbooks\\users_ready.txt', line_to_add=user)
                            logger.info(f"Process completed successfully for user {user}. Email sent with attachments: {files_to_send}.")
                            break  # Exit the retry loop if successful
                        except Exception as e:
                            sleep(time_to_retry)
                            logger.warning(f"Attempt {attempt + 1} failed for user {user}: {e}")
                            if attempt == try_attempts - 1:
                                logger.error(f"All attempts failed for user {user}. Moving to the next user.")

    def get_users(self) -> list[str]:
        users = self.txt.read_txt(txt_file='.\\workbooks\\users.txt')
        users = [user for user in users if user.strip() != '']
        self.txt.create_empty_txt(txt_file='.\\workbooks\\users_ready.txt', if_not_exists=True)
        users_ready = self.txt.read_txt(txt_file='.\\workbooks\\users_ready.txt')
        users = [user for user in users if user not in users_ready]
        logger.debug(f"AutomationCoins.get_users: returning users={users} users_ready={users_ready}")
        return users

if __name__ == '__main__':
    automationcoins = AutomationCoins(process_id='0001', process_type='rpa', process_machine='COOP_0001', necessary_apps=['calculadora'])
    automationcoins.finalize_apps()
    automationcoins.initialize_apps()
    automationcoins.manage_coins(multiply_value=3, 
                                 files_to_send=['C:\\Users\\marcos.farias\\Downloads\\CotacaoMoedas.txt', 
                                                'C:\\Users\\marcos.farias\\Downloads\\CotacaoMoedas.xlsx'])
    automationcoins.finalize_apps()
