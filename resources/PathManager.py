from os import makedirs
from loguru import logger
from resources.EnvManager import EnvManager

class PathManager:
    def __init__(self) -> None|OSError:
        """Gerencia os caminhos de diretórios necessários para o funcionamento do sistema.
        
        :returns None:
        :raises OSError: caso tenha ocorrido falha ao verificar os diretórios configurados.
        """
        self.envmanager = EnvManager()
        self.erros = {}
        self.verify_paths()
        if self.erros:
            raise OSError(f'Verificar os seguintes erros: {self.erros}')
        self.path_workbooks = self.envmanager.workbooks_path

    def verify_paths(self) -> None:
        """Verifica se os diretórios especificados existem e, caso não existam, tenta criá-los. Se não for possível criar algum diretório, registra o erro.
        
        :returns None:
        """
        for _path in self.envmanager.paths.values():
            try:
                makedirs(_path, exist_ok=True)
            except Exception as error:
                logger.error(f'Diretório "{_path}" não criado | Erro: {error}')
                self.erros[_path] = error
