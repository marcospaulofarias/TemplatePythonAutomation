from resources.Calculadora import Calculadora

if __name__ == "__main__":
    with Calculadora(name_of_program='calc.exe', name_of_process='CalculatorApp.exe') as calculadora:
        calculadora.sum_1_1()
