from resources.Txt import Txt

class DataBase:
    def __init__(self, process_id: str = None, process_type: str = None, process_machine: str = None):
        self.txt = Txt(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def get_proccesses(self) -> list[str]:
        """Função para ler arquivo txt com os processos ativos.
        
        :returns: lista de processos ativos, ex: ["processo1", "processo2", "processo3"].
        :raises RunTimeError: se houver erro ao ler o arquivo, ex: Por alguma razão o arquivo não existe.
        """
        processos = []
        for line in self.txt.read_txt(txt_file='.\\processos_random.txt'):
            processos.append(line.split(';')[:3])
        return processos

if __name__ == '__main__':
    database = DataBase(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    processos = database.get_proccesses()
    print(f'processos: {processos}')
