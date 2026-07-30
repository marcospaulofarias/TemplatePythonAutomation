from loguru import logger
import openpyxl # type: ignore
from resources.PrintAutomation import PrintAutomation
from os import path

class Xlsx:
    """Classe para manipulação de arquivos Excel (.xlsx) usando openpyxl.

    :param file_path: caminho completo do arquivo Excel a ser manipulado
    :param create_sheet: criar arquivo Excel se não existir?
    :returns None: se ocorrer nenhuma falha
    :raises RunTimeError: se não puder abrir ou criar o arquivo.
    """
    def __init__(self, file_path: str, create_xlsx: bool = False) -> None|RuntimeError:
        self.file_path = file_path
        self.printautomation = PrintAutomation()
        try:
            self.file_path = file_path
            if not path.exists(file_path) and create_xlsx:
                self.workbook = openpyxl.Workbook()
                self.save_workbook()
            elif path.exists(file_path):
                self.workbook = openpyxl.load_workbook(file_path)
        except Exception as error_x:
            logger.critical(f'O arquivo "{file_path}" não pôde ser criado.\nErro: {error_x}.')
            raise RuntimeError(f'O arquivo "{file_path}" não pôde ser criado.\nErro: {error_x}.') from error_x


    def get_sheet_names(self) -> list[str]|RuntimeError:
        """Retorna uma lista com os nomes das planilhas no arquivo Excel.
        
        :return: lista com os nomes das planilhas no arquivo.
        :raises RunTimeError: se não puder retornar os nomes das planilhas.
        """
        try:
            return self.workbook.sheetnames
        except Exception as error_x:
            logger.critical(f'Não foi possível retornar as planilhas do arquivo "{self.file_path}".\nErro: {error_x}')
            raise RuntimeError(f'Não foi possível retornar as planilhas do arquivo "{self.file_path}".') from error_x
    
    def get_sheet(self, sheet_name: str, create_sheet: bool = False) -> openpyxl.workbook|RuntimeError:
        """Retorna a planilha especificada pelo nome.

        :param sheet_name: nome da planilha a ser retornada.
        :param create_sheet: criar planilha se não existir?
        :return: objeto da planilha.
        :raises RunTimeError: se não puder criar e/ou acessar a planilha.
        """
        try:
            if sheet_name not in self.workbook.sheetnames and create_sheet:
                self.workbook.create_sheet(sheet_name)
                return self.workbook[sheet_name]
            elif sheet_name in self.workbook.sheetnames:
                return self.workbook[sheet_name]
            else:
                raise ValueError(f'Planilha "{sheet_name}" não existe no arquivo "self.file_path".')
        except Exception as error_x:
            logger.critical(f'Não foi possível retornar as planilhas do arquivo "{self.file_path}".\nErro: {error_x}')
            raise RuntimeError(f'Não foi possível retornar as planilhas do arquivo "{self.file_path}".\nErro: {error_x}') from error_x
    
    def get_cell_value(self, sheet_name: str, cell_reference: str) -> str|RuntimeError:
        """Retorna o valor da célula especificada.

        :param sheet_name: Nome da planilha que contém a célula.
        :param cell_reference: Referência da célula (ex: 'A1').
        :returns: valor da célula.
        :raises RuntimeError: se ocorrer qualquer falha.
        """
        try:
            sheet = self.get_sheet(sheet_name=sheet_name, create_sheet=False)
            return sheet[cell_reference].value
        except Exception as error_x:
            logger.critical(f'Não foi possível obter o valor da célula "{cell_reference}" na planilha "{sheet_name}".\nErro: {error_x}')
            raise RuntimeError(f'Não foi possível obter o valor da célula "{cell_reference}" na planilha "{sheet_name}".\nErro: {error_x}') from error_x
    
    def set_cell_value(self, sheet_name: str, cell_reference: str, value: any, create_sheet: bool = False) -> None|RuntimeError:
        """Define o valor da célula especificada.

        :param sheet_name: nome da planilha que contém a célula.
        :param cell_reference: referência da célula (ex: 'A1').
        :param value: valor a ser definido na célula.
        :param create: criar planilha se não existir?
        :returns None: se não ocorrer nenhuma falha.
        :raises RunTimeError: se ocorrer qualquer falha.
        """
        try:
            sheet = self.get_sheet(sheet_name=sheet_name, create_sheet=create_sheet)
            sheet.value[cell_reference] = value
        except Exception as error_x:
            logger.critical(f'Não foi possível mudar o valor da célula "{cell_reference}" para "{value}".\nErro: {error_x}.')
            raise RuntimeError(f'Não foi possível mudar o valor da célula "{cell_reference}" para "{value}".\nErro: {error_x}.') from error_x

    def save_workbook(self) -> None|RuntimeError:
        """Função para salvar o arquivo self.workbook.
        
        :returns None: se não ocorrer nenhuma falha.
        :raises RunTimeError: se ocorrer alguma falha."""
        try:
            self.workbook.save(self.file_path)
        except Exception as error_x:
            logger.critical(f'Erro ao salvar o arquivo "{self.file_path}": {error_x}')
            self.printautomation.print_error()
            raise RuntimeError(f'Erro ao salvar o arquivo "{self.file_path}": {error_x}') from error_x
