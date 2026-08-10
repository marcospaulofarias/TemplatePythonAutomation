from os import getenv
from dotenv import load_dotenv
load_dotenv()
from loguru import logger

class EnvManager:
    """Gerencia as variáveis de ambiente necessárias para o funcionamento do sistema.
    A classe carrega as variáveis de ambiente do arquivo .env e verifica se todas as variáveis necessárias estão presentes.
    
    :returns None: caso todas variáveis estejam configuradas corretamente.
    :raises EnvironmentError: caso alguma variável esteja ausente.
    """
    def __init__(self) -> None:
        logger.debug("EnvManager.__init__: carregando variáveis de ambiente")
        self.workbooks_path = getenv("PATH_WORKBOOKS")
        env_vars = (self.workbooks_path,)
        if any(var is None for var in env_vars):
            logger.critical("Algumas variáveis de ambiente não foram definidas. "
                            "Certifique-se de que todas as variáveis necessárias estão presentes no arquivo .env."
                            )
            raise EnvironmentError("Algumas variáveis de ambiente não foram definidas. "
                                   "Certifique-se de que todas as variáveis necessárias estão presentes no arquivo .env."
                                   )
        self.paths = {
            "workbooks": self.workbooks_path
        }

        self.email_users = {
            "error_email": getenv("ERROR_EMAIL")
        }
