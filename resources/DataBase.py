from resources.Txt import Txt

class DataBase:
    def __init__(self, process_id: str = None, process_type: str = None, process_machine: str = None):
        self.txt = Txt(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def get_proccesses(self) -> list[str]:
        """Função para ler arquivo txt com os processos ativos.

        Por padrão esta função retorna apenas processos que NÃO estão na
        blacklist (`.\\workbooks\\processes_ready.txt`).

        :returns: lista de processos ativos, cada item é uma lista: [id, type, machine].
        :raises RunTimeError: se houver erro ao ler o arquivo.
        """
        processos = []
        # garante que o arquivo de blacklist existe
        self.txt.create_empty_txt(txt_file='.\\workbooks\\processes_ready.txt', if_not_exists=True)
        try:
            ready_list = self.txt.read_txt(txt_file='.\\workbooks\\processes_ready.txt')
        except RuntimeError:
            ready_list = []

        for line in self.txt.read_txt(txt_file='.\\processos_random.txt'):
            parts = line.split(';')[:3]
            proc_id = parts[0] if parts else ''
            if proc_id in ready_list:
                # pula processos que já foram marcados como prontos
                continue
            processos.append(parts)
        return processos

    def mark_process_ready(self, process_id: str) -> None:
        """Marca um processo na blacklist (`workbooks/processes_ready.txt`)."""
        self.txt.add_to_txt(txt_file='.\\workbooks\\processes_ready.txt', data_to_add=[process_id], create_txt=True)

    def read_processes_ready(self) -> list[str]:
        """Retorna a lista de processos presentes em `workbooks/processes_ready.txt`."""
        self.txt.create_empty_txt(txt_file='.\\workbooks\\processes_ready.txt', if_not_exists=True)
        return self.txt.read_txt(txt_file='.\\workbooks\\processes_ready.txt')

if __name__ == '__main__':
    database = DataBase(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    processos = database.get_proccesses()
    print(f'processos: {processos}')
