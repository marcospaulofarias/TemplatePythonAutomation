 # Template Python Automation

## Visão geral

Este repositório contém uma biblioteca e conjunto de utilitários para
automação Windows baseada em Python. A intenção é prover building blocks
reutilizáveis — controles de navegador, controle de processos, captura de
prints, leitura/escrita de arquivos, integração com Outlook e logging —
que você pode integrar em flows de RPA customizados.

> Observação: os exemplos em `use_cases/` e o `main.py` são demonstrativos
> e não fazem parte da biblioteca core; a documentação abaixo descreve a
> API e os utilitários que compõem o projeto (excluindo `use_cases` e
> `main.py`).

## Componentes principais

- `resources/` — módulos de infraestrutura e helpers:
    - `Initializator.py` — inicia programas e valida processos materializados
    - `SerialKiller.py` — finaliza processos por nome (psutil + taskkill fallback)
    - `Browser.py` — helpers Selenium + UIAutomation para web navigation
    - `PrintAutomation.py` — captura screenshots e salva em `workbooks/`
    - `Txt.py` — leitura e escrita de arquivos TXT usados pelo sistema
    - `Xlsx.py` — helpers para manipular arquivos Excel (openpyxl)
    - `Outlook.py` — enviar/ler e-mails via Microsoft Outlook COM
    - `PathManager.py` — resolve caminhos (workbooks, temp, etc.)
    - `logger_config.py` — configuração central do `loguru`
    - `DataBase.py` — leitor simples de processos (pode ser substituído por orquestrador)

- `utils/` — funções utilitárias
    - `config.py` — carrega `config/apps.json` e aplica overrides via env vars
    - `date_time_utils.py` — funções de data/tempo

- `workbooks/` — arquivos gerados/consumidos pela automação (TXT, XLSX)
- `logs/` — arquivos de log gravados por `logger_config`

## Requisitos

- Windows 10/11
- Python 3.10+ (o projeto foi desenvolvido com 3.12, mas 3.10+ deve funcionar)
- Microsoft Edge + driver compatível para Selenium
- Outlook desktop (para envio via COM), se for usar `Outlook.py`
- Dependências listadas em `requirements.txt`

Instalação mínima:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure `.env` (ex.: `PATH_WORKBOOKS=./workbooks`)

## Como usar os módulos (exemplos)

Observe que estes exemplos usam apenas os módulos da pasta `resources` e
`utils` — não os `use_cases` demonstrativos.

1) Inicializar logger

```python
from resources.logger_config import configure_logger
configure_logger(process_id='0001', process_type='rpa', process_machine='COOP_0001')
```

2) Iniciar um programa (Initializator)

```python
from resources.Initializator import Initializator
init = Initializator(process_id='0001', process_type='rpa', process_machine='COOP_0001')
init.run_program(['calculadora'])
```

3) Finalizar processos (SerialKiller)

```python
from resources.SerialKiller import SerialKiller
sk = SerialKiller(process_id='0001', process_type='rpa', process_machine='COOP_0001')
sk.kill_program_by_name(['msedge'])
```

4) Capturar erro em tela e salvar (PrintAutomation)

```python
from resources.PrintAutomation import PrintAutomation
pa = PrintAutomation(process_id='0001', process_type='rpa', process_machine='COOP_0001')
pa.print_error()
```

5) Ler / gravar TXT (Txt)

```python
from resources.Txt import Txt
txt = Txt(process_id='0001', process_type='rpa', process_machine='COOP_0001')
lines = txt.read_txt('.\\workbooks\\users.txt')
txt.new_or_overwrite_txt('.\\workbooks\\out.txt', ['a','b'], create_txt=True)
```

6) Enviar e-mail (Outlook)

```python
from resources.Outlook import Outlook
out = Outlook()
out.send_email(recipients=['you@company.com'], subject='Teste', body='Corpo', attachments=['C:\\path\\file.txt'])
```

7) Browser (abrir e navegar)

```python
from resources.Browser import Browser
br = Browser(process_id='0001', process_type='rpa', process_machine='COOP_0001', headless=True)
br._open_browser()
br.get_site('https://www.example.com')
```

## Configuração de apps (`config/apps.json`)

O arquivo `config/apps.json` mapeia chaves lógicas para executáveis e nomes
de processo. Exemplo mínimo:

```json
{
    "calculadora": {
        "name_of_program": "calc.exe",
        "name_of_process": ["CalculatorApp.exe"]
    }
}
```

Você pode sobrepor `name_of_program` e `name_of_process` via variáveis de
ambiente `CALCULADORA_PROGRAM` e `CALCULADORA_PROCESS`.

## Logging

Os logs são gravados em `logs/<process_id>_<type>_<machine>.log` via
`resources/logger_config.py`. `loguru` é usado para simplicidade e nível
`DEBUG` por padrão.

## Testes

Arquivos de teste estão em `tests/`. Rode com:

```powershell
pytest -q
```

## Segurança e git

- mantenha `venv/`, `logs/` e `.env` no `.gitignore`
- não comite arquivos com dados de usuários (ex.: `workbooks/users.txt`)


## Vantagens de custo

- **Zero custo de licença**: funciona com bibliotecas open-source — sem
    pagamentos por bot ou por runtime.
- **Infraestrutura mínima**: roda em máquinas Windows existentes; não exige
    servidores proprietários nem serviços gerenciados para POCs e automações
    pequenas.
- **Baixo custo operacional**: atualizações e suporte são feitos via código
    (sem contratos caros de manutenção); time interno controla prioridades.
- **Escalabilidade econômica**: aumente capacidade com máquinas padrão e
    um banco Postgres — escala horizontal com custo variável previsível.
- **Rápido retorno (ROI)**: POCs e automações simples são implementados e
    colocados em produção rapidamente, reduzindo tempo até o benefício
    financeiro.
- **Integrações sem middleware pago**: integra com Outlook, Edge e Office
    diretamente, evitando custos de conectores comerciais.