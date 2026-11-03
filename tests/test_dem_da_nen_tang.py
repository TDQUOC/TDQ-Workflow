"""Scanner distinguishes the signatures of builtin open and Path.open."""
import importlib.util
from pathlib import Path

import pytest


_SPEC = importlib.util.spec_from_file_location(
    "dem_da_nen_tang", Path(__file__).resolve().parents[1] / "tools_kiem/dem_da_nen_tang.py")
scanner = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(scanner)


@pytest.mark.parametrize("expression, missing", [
    ('open("x", "rb")', False),
    ('open("x", "a+b")', False),
    ('open("x", mode="rb")', False),
    ('open("x")', True),
    ('open("x", "r")', True),
    ('open("x", mode="a")', True),
    ('open("x", "r", encoding="utf-8")', False),
    ('Path("x").open("rb")', False),
    ('Path("x").open("a+b")', False),
    ('Path("x").open(mode="rb")', False),
    ('Path("x").open()', True),
    ('Path("x").open("r")', True),
    ('Path("x").open(mode="a")', True),
    ('Path("x").open("r", encoding="utf-8")', False),
])
def test_open_mode_and_encoding(tmp_path, expression, missing):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "sample.py").write_text(expression + "\n", encoding="utf-8")
    findings = scanner.dem_ma_nguon(tmp_path)["open_thieu_encoding"]
    assert findings == ([str(Path("scripts/sample.py")) + ":1"] if missing else [])


def test_guarded_posix_import_is_still_an_occurrence(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "lock.py").write_text(
        'import os\nif os.name == "nt":\n    import msvcrt\nelse:\n    import fcntl\n',
        encoding="utf-8",
    )
    assert scanner.dem_ma_nguon(tmp_path)["import_chi_posix"] == [
        str(Path("scripts/lock.py")) + ":5"
    ]
