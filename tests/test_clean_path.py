import os
from resources.FilesManager import FilesManager


class _FakePrint:
	def print_error(self, *args, **kwargs):
		# noop for tests
		return None


def _patch_deps(monkeypatch):
	# FilesManager imports PathManager and PrintAutomation at module level;
	# patch them to avoid external side effects (env vars, filesystem captures).
	monkeypatch.setattr('use_cases.FilesManager.PathManager', lambda: None)
	monkeypatch.setattr('use_cases.FilesManager.PrintAutomation', lambda: _FakePrint())


def test_list_files_returns_only_files(tmp_path, monkeypatch):
	_patch_deps(monkeypatch)
	d = tmp_path / "folder"
	d.mkdir()
	# create files and a subdirectory
	f1 = d / "a.txt"
	f2 = d / "b.log"
	f1.write_text("one")
	f2.write_text("two")
	(d / "sub").mkdir()

	fm = FilesManager()
	listed = fm._list_files(str(d))
	# normalize paths and compare basenames
	basenames = {os.path.basename(os.path.normpath(p)) for p in listed}
	assert basenames == {"a.txt", "b.log"}


def test_rm_file_removes_and_silently_ignores_missing(tmp_path, monkeypatch):
	_patch_deps(monkeypatch)
	f = tmp_path / "temp.txt"
	f.write_text("x")

	fm = FilesManager()
	# remove existing file
	fm._rm_file(str(f))
	assert not f.exists()

	# removing non-existing file should not raise
	fm._rm_file(str(f))


def test_clean_paths_clears_directory(tmp_path, monkeypatch):
	_patch_deps(monkeypatch)
	d = tmp_path / "to_clean"
	d.mkdir()
	(d / "one.txt").write_text("1")
	(d / "two.txt").write_text("2")

	fm = FilesManager()
	fm.clean_paths([str(d)])

	# directory should contain no files (subdirs may remain)
	remaining = [p for p in os.listdir(str(d))]
	assert all(not os.path.isfile(os.path.join(str(d), name)) for name in remaining)

