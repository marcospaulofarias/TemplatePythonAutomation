from loguru import logger
from pathlib import Path
from resources.FilesManager import FilesManager
from time import monotonic

class Txt:
    """Classe para lidar com arquivos txt.
    
    :param process_id: Identificador do processo para logs e rastreamento.
    :param process_type: Tipo do processo para logs e rastreamento.
    :param process_machine: Nome da máquina para logs e rastreamento.
    :returns None:
    """
    def __init__(self, process_id: str, process_type: str, process_machine: str) -> None:
        logger.debug(f"Txt.__init__: process_id={process_id} process_type={process_type} process_machine={process_machine}")
        self.filesmanager = FilesManager(process_id=process_id, process_type=process_type, process_machine=process_machine)
        
    def read_txt(self, txt_file: str) -> list[str]:
        """Função para ler arquivo txt.
        
        :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
        :returns: linhas do txt em forma de lista, ex: ["linha1", "linha2", "linha3"].
        :raises RunTimeError: se houver erro ao ler o arquivo, ex: Por alguma razão o arquivo não existe.
        """
        logger.debug(f"Txt.read_txt: txt_file={txt_file}")
        try:
            with open(file=txt_file, mode='r', encoding='utf-8') as opened_txt:
                lines = [line.replace("\n", "") for line in opened_txt.readlines()]
            logger.debug(f"Txt.read_txt: {len(lines)} linhas lidas")
            return lines
        except Exception as error_x:
            logger.critical(f'Erro ao ler o arquivo "{txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao ler o arquivo "{txt_file}".\nErro: {error_x}') from error_x

    def add_to_txt(self, txt_file: str, data_to_add: list[str], create_txt: bool) -> None:
        """Função para adicionar conteúdo a um arquivo existente.
        
        :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
        :param create_txt: criar arquivo txt se não existir? ex: True.
        :returns None:
        :raises RunTimeError: se houver erro ao adicionar dado oo arquivo, ex: Por alguma razão o arquivo não existe.
        """
        logger.debug(f"Txt.add_to_txt: txt_file={txt_file} create_txt={create_txt} data_to_add={data_to_add}")
        if create_txt:
            self._create_txt(txt_file=txt_file)
        try:
            with open(file=txt_file, mode='a', encoding='utf-8') as opened_txt:
                opened_txt.writelines(f'{line}\n' for line in data_to_add)
            logger.debug(f"Txt.add_to_txt: adicionado {len(data_to_add)} linhas")
        except Exception as error_x:
            logger.critical(f'Erro ao adicionar o conteúdo de "data_to_add" ao arquivo "{txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao adicionar o conteúdo de "data_to_add" ao arquivo "{txt_file}".\nErro: {error_x}.') from error_x

    def new_or_overwrite_txt(self, txt_file: str, data_to_overwrite: list[str], create_txt: bool) -> None:
        """Função para sobrescrever os dados de um arquivo.
        
        :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
        :param create_txt: criar arquivo txt se não existir? ex: True.
        :returns None:
        :raises RunTimeError: se houver erro ao sobrescrever o arquivo, ex: Por alguma razão o arquivo não existe.
        """
        logger.debug(f"Txt.new_or_overwrite_txt: txt_file={txt_file} create_txt={create_txt} data_to_overwrite_len={len(data_to_overwrite)}")
        if create_txt:
            self._create_txt(txt_file=txt_file)
        try:
            with open(file=txt_file, mode='w', encoding='utf-8') as opened_txt:
                opened_txt.writelines(f'{line}\n' for line in data_to_overwrite)
            logger.debug(f"Txt.new_or_overwrite_txt: gravado {len(data_to_overwrite)} linhas")
        except Exception as error_x:
            logger.critical(f'Erro ao sobrescrever com o conteúdo "data_to_overwrite" o arquivo "{txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao sobrescrever com o conteúdo "data_to_overwrite" o arquivo "{txt_file}".\nErro: {error_x}.') from error_x

    def create_empty_txt(self, txt_file: str, if_not_exists: bool = True) -> None:
        """Função para criar um arquivo txt vazio.
        
        :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
        :param if_not_exists: criar arquivo txt se não existir? ex: True.
        :returns None:
        :raises RunTimeError: se houver erro ao criar o arquivo, ex: Diretório do arquivo não existe.
        """
        logger.debug(f"Txt.create_empty_txt: txt_file={txt_file} if_not_exists={if_not_exists}")
        if if_not_exists and self.filesmanager.verify_exists_file(txt_file):
            logger.info(f'O arquivo "{txt_file}" já existe. Nenhuma ação foi tomada.')
            return
        self._create_txt(txt_file=txt_file)

    def _create_txt(self, txt_file: str, time_limit_to_create: float = 3) -> None:
        """Função para criar o arquivo necessário.
        
        :param txt_file: arquivo txt "{caminho}+{nome_arquivo.txt}".
        :param time_limit_to_create: tempo limite em segundos para criar o arquivo.
        :returns None:
        :raises RunTimeError: erro ao criar o arquivo, ex: Diretório do arquivo não existe.
        """
        logger.debug(f"Txt._create_txt: txt_file={txt_file} time_limit_to_create={time_limit_to_create}")
        try:
            Path(txt_file).touch()
            time_1 = monotonic()
            while not self.filesmanager.verify_exists_file(txt_file):
                if monotonic() - time_1 >= time_limit_to_create:
                    raise RuntimeError(f'Tempo limite de {time_limit_to_create} segundos excedido ao tentar criar o arquivo "{txt_file}".')
            logger.info(f'Arquivo "{txt_file}" criado com sucesso.')
        except Exception as error_x:
            logger.critical(f'Erro ao criar o arquivo "{txt_file}".\nErro: {error_x}.')
            raise RuntimeError(f'Erro ao criar o arquivo "{txt_file}".\nErro: {error_x}.') from error_x

if __name__ == '__main__':
    txt_file = '.\\workbooks\\teste_01.txt'
    txt = Txt(process_id='0001', process_type='rpa', process_machine='COOP_0001')

    txt.add_to_txt(txt_file=txt_file, data_to_add=["add1", "add2", "add3", "add4", "add5", "add6", "add7", "add8", "add9", "add10"], create_txt=True)
    txt_read = txt.read_txt(txt_file=txt_file)
    logger.debug(f'TXT_READ_2: {txt_read}')

    txt.new_or_overwrite_txt(txt_file=txt_file, data_to_overwrite=["overwrite1", "overwrite2", "overwrite3", "overwrite4", "overwrite5", "overwrite6", "overwrite7", "overwrite8", "overwrite9", "overwrite10"], create_txt=False)
    txt_read = txt.read_txt(txt_file=txt_file)
    logger.debug(f'TXT_READ_3: {txt_read}')

    txt.new_or_overwrite_txt(txt_file=txt_file, data_to_overwrite=[], create_txt=False)
    txt_read = txt.read_txt(txt_file=txt_file)
    logger.debug(f'TXT_READ_4: {txt_read}')
