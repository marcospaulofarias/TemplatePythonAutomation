import json
import os
from typing import Dict, Any


def load_apps_config(path: str = None) -> Dict[str, Any]:
    """Carrega a configuração de apps a partir de um arquivo JSON e aplica overrides do .env.

    Overrides por variável de ambiente seguem o padrão <APPKEY>_PROGRAM e <APPKEY>_PROCESS,
    onde <APPKEY> é o nome da chave em maiúsculas (ex: CALCULADORA_PROGRAM).
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "apps.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            apps = json.load(f)
    except FileNotFoundError:
        return {}

    # Aplicar overrides via env
    for key, cfg in apps.items():
        up = key.upper()
        program_env = os.getenv(f"{up}_PROGRAM")
        process_env = os.getenv(f"{up}_PROCESS")
        if program_env:
            cfg["name_of_program"] = program_env
        if process_env:
            cfg["name_of_process"] = process_env
    return apps
