from pathlib import Path
from loguru import logger
from resources.PathManager import PathManager
from resources.logger_config import configure_logger
from utils.date_time_utils import get_numeric_timestamp
import uiautomation as auto

class PrintAutomation:
    def __init__(self, process_id: str = "", process_type: str = "", process_machine: str = "") -> None:
        """Contexto da execução (process_id/type/machine) entra na construção e
        prefixa o nome dos screenshots; os defaults vazios mantêm compatível quem
        não tem contexto para passar.
        
        :returns None:
        """
        self.pathmanager = PathManager()
        self.process_id = process_id
        self.process_type = process_type
        self.process_machine = process_machine
        configure_logger(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def _build_save_path(self) -> str:
        """Retorna o nome do caminho+nome_do_arquivo a ser gerado com base nas informações do processo, data e hora.
        
        :returns: str(caminho_do_arquivo+nome_do_arquivo) a ser gerado.
        """
        parts = [p for p in (self.process_id, self.process_type, self.process_machine) if p]
        file_name = "_".join(parts + [get_numeric_timestamp()])
        return str(Path(self.pathmanager.path_workbooks) / f"{file_name}.png")

    def print_error(self, element_to_print: auto.Control = None) -> None:
        """Tira um print da tela no momento do erro e salva contendo as informações do processo, data e hora.
        
        :returns None
        """
        try:
            if element_to_print:
                target = element_to_print
                target.CaptureToImage(savePath=self._build_save_path())
            auto.GetRootControl().CaptureToImage(savePath=self._build_save_path())
        except Exception as error:
            logger.warning(f"Falha ao capturar do elemento, tentando tela cheia: {error}")
            try:
                auto.GetRootControl().CaptureToImage(savePath=self._build_save_path())
            except Exception as error_fallback:
                logger.error(f"Falha também no print de tela cheia: {error_fallback}")
