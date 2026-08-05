from use_cases.AutomationCoins import AutomationCoins
from resources.DataBase import DataBase

if __name__ == '__main__':
    database = DataBase()
    processes = database.get_proccesses()

    if processes:
        for process in processes:
            process_id, process_type, process_machine = process

            automationcoins = AutomationCoins(process_id=process_id, process_type=process_type, process_machine=process_machine, necessary_apps=['calculadora'])
            automationcoins.run(files_to_send=[f'C:\\Users\\user\\Downloads\\CotacaoMoedas{process_id}.txt', 
                                            f'C:\\Users\\user\\Downloads\\CotacaoMoedas{process_id}.xlsx'], 
                                            multiply_value=3, try_attempts=3)
    