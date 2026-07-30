from os import listdir, path
import os
import shutil
from resources.PathManager import PathManager
from resources.PrintAutomation import PrintAutomation

class FilesManager:
    def __init__(self) -> None:
        """Classe para gerenciamento de arquivos.
        
        :returns None:
        """
        self.pathmanager = PathManager()
        self.printautomation = PrintAutomation()

    def _list_files(self, directory: str) -> list|RuntimeError:
        """Lista todos os arquivos em um diretório específico.
        
        :param directory: Caminho completo do diretório a ser listado.
        :returns: Lista de caminhos completos dos itens (arquivos e subdiretórios) no diretório.
        :raises RunTimeError: caso ocorra algum erro ao listar os arquivos, ex: diretório inexistente."""
        try:
            return [os.path.join(directory, file_name) for file_name in listdir(directory)]
        except Exception as e:
            self.printautomation.print_error(f"Erro ao tentar listar arquivos no diretório {directory}: {e}")
            raise RuntimeError(f"Erro ao tentar listar arquivos no diretório {directory}: {e}")

    def _rm_file(self, file_to_remove: str) -> None:
        """Remove um arquivo específico.
        
        :param file_to_remove: Caminho completo + arquivo a ser removido.
        :returns None:
        :raises RunTimeError: caso não um arquivo exista e não foi possível remove-lo."""
        try:
            # remove files or remove directories recursively
            if os.path.isdir(file_to_remove):
                shutil.rmtree(file_to_remove)
            else:
                os.remove(file_to_remove)
        except FileNotFoundError:
            ...  # Se o arquivo não existir, não faz nada
        except Exception as e:
            self.printautomation.print_error(f"Erro ao tentar remover o arquivo {file_to_remove}: {e}")
            raise RuntimeError(f"Erro ao tentar remover o arquivo {file_to_remove}: {e}")
        
    def clean_paths(self, paths_to_clean: list) -> None|RuntimeError:
        """Limpa os diretórios especificados, removendo todos os arquivos dentro deles.
        
        :param paths_to_clean: Lista de caminhos completos dos diretórios a serem limpos.
        :returns None:
        :raises RunTimeError: caso o diretório não tenha sido parcial ou completamente limpo, isto é, todas pastas e arquivos dentro deste diretório não tenham sido excluídas."""
        for dir_path in paths_to_clean:
            try:
                for file_name in listdir(dir_path):
                    full_path = os.path.join(dir_path, file_name)
                    if os.path.isfile(full_path):
                        self._rm_file(full_path)
            except Exception as e:
                self.printautomation.print_error(f"Erro ao tentar limpar o diretório {dir_path}: {e}")
                raise RuntimeError(f"Erro ao tentar limpar o diretório {dir_path}: {e}")