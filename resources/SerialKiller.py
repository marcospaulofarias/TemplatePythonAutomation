from typing import Literal
from utils.config import load_apps_config
from resources.PrintAutomation import PrintAutomation
import psutil
from loguru import logger
import subprocess
from os import getenv

class SerialKiller:
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
        logger.debug(f"SerialKiller.__init__: process_id={process_id} process_type={process_type} process_machine={process_machine}")
        self.printautomation = PrintAutomation(process_id=self.process_id, 
                                                       process_type=self.process_type, 
                                                       process_machine=self.process_machine)
        self.executable_apps = load_apps_config()

    def kill_program_by_name(self, programs_to_kill: list[str] = None, timeout: float = 10, user_to_kill: str | None = None) -> Literal[True]:
        """Função para finalizar um ou mais programas pelo nome conforme configurado em apps.json, ex: ["calculadora"].

        :param programs_to_kill: nomes dos programas a serem finalizados conforme arquivo de configuração apps.json, ex: ["calculadora", "msedge"], 
        se não for passado parâmetro, finalizará todos os programas configurados.
        :param timeout: tempo (s) a aguardar o processo encerrar após o terminate/kill
        :returns True: se todos os programas forem finalizados.
        :raises RunTimeError: se ocorrer qualquer falha.
        """
        if user_to_kill is None:
            user_to_kill = f'{getenv("USERDOMAIN")}\\{getenv("USERNAME")}'
        logger.debug(f"SerialKiller.kill_program_by_name: programs_to_kill={programs_to_kill} timeout={timeout} user_to_kill={user_to_kill}")
        if not programs_to_kill:
            programs_to_kill = self.executable_apps.keys()
        for program_to_kill in programs_to_kill:
            logger.debug(f"SerialKiller.kill_program_by_name: program_to_kill={program_to_kill}")
            process = self.executable_apps.get(program_to_kill)
            if process:
                name_of_processes = process.get("name_of_process")
                for name_of_process in name_of_processes:
                    logger.debug(f"SerialKiller.kill_program_by_name: checking process {name_of_process}")
                    try:
                        procs = [p for p in psutil.process_iter(['name', 'username']) if p.info['name'] == name_of_process and p.info["username"] == user_to_kill]
                        if not procs:
                            logger.warning(f'Nenhum processo "{name_of_process}" encontrado em execução')
                            continue
                        for proc in procs:
                            proc.terminate()
                            logger.info(f'Programa "{name_of_process}" finalizado com sucesso!')
                    except psutil.AccessDenied:
                        result_kill = subprocess.run([
                            "taskkill",
                            "/F",
                            "/IM",
                            name_of_process,
                            "/FI",
                            f"USERNAME eq {user_to_kill}"
                        ],
                            capture_output=True,
                            text=True,
                            timeout=timeout
                        )
                        if result_kill.returncode == 0:
                            logger.info(f'Programa "{name_of_process}" finalizado com sucesso!')
                            continue
                        else:
                            self.printautomation.print_error()
                            logger.critical(f'O programa "{name_of_process}" não pôde ser finalizado. Verificar possível erro.')
                            raise RuntimeError(f'O programa "{name_of_process}" não pôde ser finalizado. Verificar possível erro.')
                    except Exception as error_x:
                        self.printautomation.print_error()
                        logger.critical(f'O processo "{name_of_process}" não pôde ser finalizado\nError: {error_x}')
                        raise RuntimeError(f'O processo "{name_of_process}" não pôde ser finalizado\nError: {error_x}') from error_x
        return True

if __name__ == '__main__':
    serialkiller = SerialKiller(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    # serialkiller.kill_program_by_name()
