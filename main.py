from use_cases.AutomationCoins import AutomationCoins
from resources.DataBase import DataBase
from loguru import logger

if __name__ == '__main__':
    database = DataBase()
    processes = database.get_proccesses()

    if processes:
        for process in processes:
            process_id, process_type, process_machine = process

            automationcoins = AutomationCoins(process_id=process_id, process_type=process_type, process_machine=process_machine, necessary_apps=['calculadora'])
            try:
                automationcoins.run(files_to_send=[f'C:\\Users\\user\\Downloads\\CotacaoMoedas{process_id}.txt', 
                                                f'C:\\Users\\user\\Downloads\\CotacaoMoedas{process_id}.xlsx'], 
                                                multiply_value=3, try_attempts=3)
                # marca o processo como pronto (blacklist) apenas quando a execução terminar sem exceção
                database.mark_process_ready(process_id)
                logger.info(f'Process {process_id} marked as ready in processes_ready.txt')
            except Exception as e:
                logger.error(f'Error running process {process_id}: {e}')
    