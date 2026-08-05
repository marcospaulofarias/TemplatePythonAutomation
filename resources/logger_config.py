from pathlib import Path
from loguru import logger

_configured_log_paths = set()


def configure_logger(process_id: str = "", process_type: str = "", process_machine: str = "", log_dir: str = ".\\logs") -> None:
    """Configura o logger global para gravar em arquivo.

    :param process_id: Identificador do processo.
    :param process_type: Tipo do processo.
    :param process_machine: Máquina do processo.
    :param log_dir: Diretório onde o arquivo de log será criado.
    :returns: None
    """
    parts = [p for p in (process_id, process_type, process_machine) if p]
    file_name = "_".join(parts) if parts else "default"
    log_path = Path(log_dir) / f"{file_name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = str(log_path)

    if log_file not in _configured_log_paths:
        logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
        _configured_log_paths.add(log_file)
