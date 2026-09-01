"""Camada de leitura de arquivos de processo para filas e blacklist."""

from resources.Txt import Txt


class DataBase:
    """Representa a base local de processos ativos e já processados.

    Este módulo usa os arquivos de texto como simulação de base de dados
    operacional. A ideia é gerenciar uma lista de processos disponíveis e uma
    blacklist para evitar reprocessamento de itens já concluidos.
    """

    def __init__(self, process_id: str = None, process_type: str = None, process_machine: str = None):
        """Inicializa a abstração de arquivos do controlador de processos."""
        self.txt = Txt(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def get_proccesses(self) -> list[str]:
        """Lê a fila de processos ativos, ignorando os itens já concluídos.

        Por padrão, esta função retorna apenas os processos que ainda não foram
        marcados como prontos na blacklist ``.\workbooks\processes_ready.txt``.

        :returns: lista de processos ativos em formato de lista [id, type, machine].
        :raises RunTimeError: se houver erro ao ler os arquivos.
        """
        processos = []
        # Garante que a blacklist exista antes da leitura para evitar falha no fluxo.
        self.txt.create_empty_txt(txt_file='.\\workbooks\\processes_ready.txt', if_not_exists=True)
        try:
            ready_list = self.txt.read_txt(txt_file='.\\workbooks\\processes_ready.txt')
        except RuntimeError:
            ready_list = []

        for line in self.txt.read_txt(txt_file='.\\processos_random.txt'):
            parts = line.split(';')[:3]
            proc_id = parts[0] if parts else ''
            if proc_id in ready_list:
                # Ignora processos já concluídos ou marcados como prontos.
                continue
            processos.append(parts)
        return processos

    def mark_process_ready(self, process_id: str) -> None:
        """Marca um processo como concluído na blacklist."""
        self.txt.add_to_txt(txt_file='.\\workbooks\\processes_ready.txt', data_to_add=[process_id], create_txt=True)

    def read_processes_ready(self) -> list[str]:
        """Retorna os identificadores de processos já marcados como prontos."""
        self.txt.create_empty_txt(txt_file='.\\workbooks\\processes_ready.txt', if_not_exists=True)
        return self.txt.read_txt(txt_file='.\\workbooks\\processes_ready.txt')


if __name__ == '__main__':
    database = DataBase(process_id='0001', process_type='rpa', process_machine='COOP_0001')
    processos = database.get_proccesses()
    print(f'processos: {processos}')
