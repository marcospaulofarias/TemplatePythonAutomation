from use_cases.AutomationCoins import AutomationCoins

if __name__ == '__main__':
    automationcoins = AutomationCoins(process_id='0001', process_type='rpa', process_machine='COOP_0001', necessary_apps=['calculadora'])
    automationcoins.run(files_to_send=['C:\\Users\\marcos.farias\\Downloads\\CotacaoMoedas.txt', 
                                       'C:\\Users\\marcos.farias\\Downloads\\CotacaoMoedas.xlsx'], 
                                       multiply_value=3, try_attempts=3)
    