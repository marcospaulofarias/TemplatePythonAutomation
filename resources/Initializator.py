import subprocess
import time
import psutil
from loguru import logger
from resources.PrintAutomation import PrintAutomation
from utils.config import load_apps_config

class Initializator:
    """Classe para finalização de processos.
    
    :param process_id: id do processo relacionado a finalização.
    :param process_type: tipo do processo relacionado a finalização.
    :param process_machine: máquina relacionada ao processo usado.
    :returns None:
    """
    def __init__(self, process_id: str, process_type: str, process_machine: str) -> None:
        self.process_id = process_id
        self.process_type = process_type
        self.process_machine = process_machine
        self.printautomation = PrintAutomation(process_id=self.process_id, 
                                               process_type=self.process_type, 
                                               process_machine=self.process_machine)
        self.executable_apps = load_apps_config()

    def run_program(self, programs_to_execute: list[str] = None, wait_existing: float = 10) -> True|ValueError|RuntimeError:
        """Executa um programa no Windows.

        :param programs_to_execute: nomes dos programas a serem executados conforme arquivo de configuração apps.json, ex: ['calculadora', 'msedge'].
            materializam outro processo (ex: abrir 'calc.exe' resulta em 'CalculatorApp.exe').
            Quando informado, é usado para finalizar instâncias em close_existing.
        :param wait_existing: tempo máximo (s) a aguardar o processo alvo aparecer assim verificando se está executando com sucesso.
            0 (padrão) não espera. Útil ao reabrir em sequência rápida um app stub/UWP que
            demora a materializar o processo real (evita matar 'antes do tempo').
        :returns True: se o programa foi iniciado com sucesso
        :returns False: se o programa não foi executado ou se houve erro na execução.
        :raises ValueErros: se o programa não foi configurado no arquivo apps.json.
        :raises RunTimeError: se o programa não pôde ser executado com sucesso.
        """
        for program_to_execute in programs_to_execute:
            program = self.executable_apps.get(program_to_execute, None)
            if program:
                name_of_program = program.get("name_of_program")
                name_of_process = program.get("name_of_process")
                try:
                    self.program_in_execute = subprocess.Popen(name_of_program)
                    # Aqui verifica se o programa está sendo executado com sucesso.
                    if wait_existing:
                        self._wait_for_process(name_of_process, timeout=wait_existing)
                except Exception as error_x:
                    logger.critical(f'O programa "{name_of_program}" não pôde ser executado\nError: {error_x}')
                    self.printautomation.print_error()
                    raise RuntimeError(f'O programa "{name_of_program}" não pôde ser executado\nError: {error_x}') from error_x
            else:
                logger.critical(f'Program "{programs_to_execute}" não configurado. Verificar arquivo "config\\apps.json"')
                raise ValueError(f'Program "{programs_to_execute}" não configurado. Verificar arquivo "config\\apps.json"')
        return True

    def _wait_for_process(self, process_name: str, timeout: float = 5, interval: float = 0.2) -> True|RuntimeError:
        """Aguarda um processo aparecer em execução.

        :param process_name: nome do processo a aguardar (ex: 'CalculatorApp.exe').
        :param timeout: tempo máximo (s) de espera.
        :param interval: intervalo (s) entre as verificações.
        :returns True: se o processo apareceu dentro do timeout. 
        :raises RunTimeError: se o processo não apareceu dentro do timeout.
        """
        fim = time.monotonic() + timeout
        while time.monotonic() < fim:
            if any(p.info['name'] == process_name for p in psutil.process_iter(['name'])):
                return True
            time.sleep(interval)
        self.printautomation.print_error()
        raise RuntimeError(f'O processo "{process_name}" não apareceu dentro do timeout')

if __name__ == '__main__':
    initializator = Initializator(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    print(initializator.executable_apps)
    initializator.run_program(programs_to_execute=["calculadora", "msedge", ])
