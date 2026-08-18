from pathlib import Path
from loguru import logger
from resources.PathManager import PathManager
from resources.logger_config import configure_logger
from utils.date_time_utils import get_numeric_timestamp
import uiautomation as auto
from resources.Outlook import Outlook
from typing import Optional, Dict, Tuple
from resources.EnvManager import EnvManager

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
        self.env_manager = EnvManager()
        self.outlook = Outlook(process_id=process_id, process_type=process_type, process_machine=process_machine)
        configure_logger(process_id=process_id, process_type=process_type, process_machine=process_machine)

    def _build_save_path(self) -> Tuple[Path, Path]:
        """Retorna o nome do caminho+nome_do_arquivo a ser gerado com base nas informações do processo, data e hora.
        
        :returns: str(caminho_do_arquivo+nome_do_arquivo) a ser gerado.
        """
        parts = [p for p in (self.process_id, self.process_type, self.process_machine) if p]
        file_name = "_".join(parts + [get_numeric_timestamp()])
        element_path = Path(self.pathmanager.path_workbooks) / f"ELEMENT_SCREEN_{file_name}.png"
        full_path = Path(self.pathmanager.path_workbooks) / f"FULL_SCREEN_{file_name}.png"
        return element_path, full_path

    def print_error(self, element_to_print: auto.Control = None, send_email: bool = False) -> Dict[str, Optional[str]]:
        """Tira um print da tela no momento do erro e salva contendo as informações do processo, data e hora.
        
        :returns None
        """
        element_file_save_path, full_file_save_path = self._build_save_path()

        # garante que os diretórios existem
        try:
            element_file_save_path.parent.mkdir(parents=True, exist_ok=True)
            full_file_save_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.exception("Falha ao garantir diretório de destino para screenshots")

        result: Dict[str, Optional[str]] = {"element": None, "full": None}

        # captura do elemento (se houver) e captura de tela cheia
        try:
            if element_to_print:
                try:
                    element_to_print.CaptureToImage(savePath=str(element_file_save_path))
                    result["element"] = str(element_file_save_path)
                except Exception:
                    logger.exception("Falha ao capturar elemento; prosseguindo para captura de tela cheia")

            try:
                auto.GetRootControl().CaptureToImage(savePath=str(full_file_save_path))
                result["full"] = str(full_file_save_path)
            except Exception:
                logger.exception("Falha ao capturar tela cheia")

            # envio de e-mail isolado para não propagar falhas
            if send_email:
                try:
                    attachments = [p for p in (result.get("element"), result.get("full")) if p]
                    if attachments:
                        self.outlook.send_email(
                            recipients=['user@example.com'],  # Replace with config/param
                            subject=f'Error in Process {self.process_id}',
                            body='An error occurred during the process execution.',
                            attachments=attachments
                        )
                except Exception:
                    logger.exception("Falha ao enviar email de notificação")

        except Exception:
            logger.exception("Erro inesperado na rotina de captura de screenshots")
            # tentativa de fallback: captura de tela cheia
            try:
                auto.GetRootControl().CaptureToImage(savePath=str(full_file_save_path))
                result["full"] = str(full_file_save_path)
            except Exception:
                logger.exception("Falha também no fallback de captura de tela cheia")

        return result
