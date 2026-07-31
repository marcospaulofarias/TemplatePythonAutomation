from loguru import logger
from pathlib import Path
from resources.FilesManager import FilesManager

class Txt:
    """Classe para lidar com arquivos txt.
    
    :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
    :param process_id: Identificador do processo para logs e rastreamento.
    :param process_type: Tipo do processo para logs e rastreamento.
    :param process_machine: Nome da máquina para logs e rastreamento.
    :param create_txt: criar arquivo txt se não existir? ex: True.
    :returns None:
    """
    def __init__(self, txt_file: str, process_id: str, process_type: str, process_machine: str, create_txt: bool = False) -> None:
        self.txt_file = txt_file
        self.filesmanager = FilesManager(process_id=process_id, process_type=process_type, process_machine=process_machine)
        if create_txt:
            self.ensure_exists()

    def ensure_exists(self) -> None:
        """Garante que o arquivo txt existe, criando-o caso necessário.
        
        :returns None:
        """
        if not self.filesmanager.verify_exists_file(self.txt_file):
            self._create_txt()

    def read_txt(self) -> list[str]:
        """Função para ler arquivo txt.
        
        :returns: linhas do txt em forma de lista, ex: ["linha1", "linha2", "linha3"].
        :raises RunTimeError: se houver erro ao ler o arquivo, ex: Por alguma razão o arquivo não existe.
        """
        try:
            with open(file=self.txt_file, mode='r', encoding='utf-8') as opened_txt:
                return [line.replace("\n", "") for line in opened_txt.readlines()]
        except Exception as error_x:
            logger.critical(f'Erro ao ler o arquivo "{self.txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao ler o arquivo "{self.txt_file}".\nErro: {error_x}') from error_x

    def add_to_txt(self, data_to_add: list[str]) -> None:
        """Função para adicionar conteúdo a um arquivo existente.
        
        :returns None:
        :raises RunTimeError: se houver erro ao adicionar dado oo arquivo, ex: Por alguma razão o arquivo não existe.
        """
        try:
            with open(file=self.txt_file, mode='a', encoding='utf-8') as opened_txt:
                opened_txt.writelines(f'{line}\n' for line in data_to_add)
        except Exception as error_x:
            logger.critical(f'Erro ao adicionar o conteúdo de "data_to_add" ao arquivo "{self.txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao adicionar o conteúdo de "data_to_add" ao arquivo "{self.txt_file}".\nErro: {error_x}.') from error_x

    def overwrite_txt(self, data_to_overwrite: list[str]) -> None:
        """Função para sobrescrever os dados de um arquivo.
        
        :returns None:
        :raises RunTImeError: se houver erro ao sobrescrever o arquivo, ex: Por alguma razão o arquivo não existe.
        """
        try:
            with open(file=self.txt_file, mode='w', encoding='utf-8') as opened_txt:
                opened_txt.writelines(f'{line}\n' for line in data_to_overwrite)
        except Exception as error_x:
            logger.critical(f'Erro ao sobrescrever com o conteúdo "data_to_overwrite" o arquivo "{self.txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao sobrescrever com o conteúdo "data_to_overwrite" o arquivo "{self.txt_file}".\nErro: {error_x}.') from error_x
        

    def _create_txt(self) -> None:
        """Função para criar o arquivo necessário.
        
        :returns None:
        :raises RunTimeError: erro ao criar o arquivo, ex: Diretório do arquivo não existe.
        """
        try:
            Path(self.txt_file).touch()
        except Exception as error_x:
            logger.critical(f'Erro ao criar o arquivo "{self.txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao criar o arquivo "{self.txt_file}".\nErro: {error_x}.') from error_x

if __name__ == '__main__':
    txt = Txt(txt_file='.\\workbooks\\teste_01.txt', process_id='0001', process_type='rpa', process_machine='COOP_0001', create_txt=True)
    txt_read = txt.read_txt()
    print(f'TXT_READ_1: {txt_read}')
    txt.add_to_txt(data_to_add=["add1", "add2", "add3", "add4", "add5", "add6", "add7", "add8", "add9", "add10"])
    txt_read = txt.read_txt()
    print(f'TXT_READ_2: {txt_read}')
    txt.overwrite_txt(data_to_overwrite=["overwrite1", "overwrite2", "overwrite3", "overwrite4", "overwrite5", "overwrite6", "overwrite7", "overwrite8", "overwrite9", "overwrite10"])
    txt_read = txt.read_txt()
    print(f'TXT_READ_3: {txt_read}')
    txt.overwrite_txt(data_to_overwrite=[])
    txt_read = txt.read_txt()
    print(f'TXT_READ_4: {txt_read}')
