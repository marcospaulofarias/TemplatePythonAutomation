import os
from resources.FilesManager import FilesManager


class _FakePrint:
    def print_error(self, *args, **kwargs):
        return None


def _patch_deps(monkeypatch):
    # Substitui as classes por construtores fake que aceitam quaisquer args
    monkeypatch.setattr('resources.FilesManager.PathManager', lambda *a, **kw: None)
    monkeypatch.setattr('resources.FilesManager.PrintAutomation', lambda *a, **kw: _FakePrint())


def test_list_files_returns_files_and_dirs(tmp_path, monkeypatch):
    _patch_deps(monkeypatch)
    d = tmp_path / "folder"
    d.mkdir()
    f1 = d / "a.txt"
    f2 = d / "b.log"
    f1.write_text("one")
    f2.write_text("two")
    (d / "sub").mkdir()

    fm = FilesManager(process_id='0001', process_type='RPA', process_machine='COOP_0001')
    listed = fm._list_files(str(d))
    basenames = {os.path.basename(os.path.normpath(p)) for p in listed}
    assert basenames == {"a.txt", "b.log", "sub"}


def test_rm_file_removes_and_silently_ignores_missing(tmp_path, monkeypatch):
    _patch_deps(monkeypatch)
    f = tmp_path / "temp.txt"
    f.write_text("x")

    fm = FilesManager(process_id='0001', process_type='RPA', process_machine='COOP_0001')
    fm._rm_file(str(f))
    assert not f.exists()

    fm._rm_file(str(f))  # não deve lançar exceção


def test_clean_paths_clears_directory(tmp_path, monkeypatch):
    _patch_deps(monkeypatch)
    d = tmp_path / "to_clean"
    d.mkdir()
    (d / "one.txt").write_text("1")
    (d / "two.txt").write_text("2")

    fm = FilesManager(process_id='0001', process_type='RPA', process_machine='COOP_0001')
    fm.clean_paths([str(d)])

    remaining = os.listdir(str(d))
    assert all(not os.path.isfile(os.path.join(str(d), name)) for name in remaining)