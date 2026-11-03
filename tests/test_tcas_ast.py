"""
Unit tests for TCAS AST Import Dependency Graph and Collision Detection in tdq_team.py
"""

import os
import sys
from pathlib import Path

# Add scripts to sys.path
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from tdq_team import (  # pyright: ignore[reportMissingImports]
    extract_ast_imports,
    file_to_module_names,
    detect_tcas_collision,
    _dot_som_nhat,
    Task,
)


def test_extract_ast_imports(tmp_path: Path):
    """Verify ast.parse extracts all variants of imports correctly."""
    py_code = """
import os
import sys
import json.decoder
from pathlib import Path
from math import sqrt, pi
from my_package.submodule import helper
"""
    py_file = tmp_path / "sample_imports.py"
    py_file.write_text(py_code, encoding="utf-8")

    imports = extract_ast_imports(str(py_file))
    assert "os" in imports
    assert "sys" in imports
    assert "json" in imports
    assert "json.decoder" in imports
    assert "pathlib" in imports
    assert "math" in imports
    assert "my_package" in imports
    assert "my_package.submodule" in imports


def test_file_to_module_names():
    """Verify conversion of file paths to importable module tokens."""
    names = file_to_module_names("hooks/scripts/stop_batch_checker.py")
    assert "stop_batch_checker" in names
    assert "hooks.scripts.stop_batch_checker" in names
    assert "scripts.stop_batch_checker" in names

    non_py = file_to_module_names("docs/README.md")
    assert non_py == set()


def test_detect_tcas_collision_direct_and_semantic(tmp_path: Path):
    """Verify collision detector spots both direct path overlaps and semantic AST imports."""
    # Case 1: Direct file collision
    collided, reason = detect_tcas_collision(["a.py", "b.py"], ["b.py", "c.py"], project_root=str(tmp_path))
    assert collided
    assert "Direct file collision" in reason

    # Case 2: Clean independent tasks
    mod_a = tmp_path / "module_alpha.py"
    mod_a.write_text("def alpha(): return 1\n", encoding="utf-8")
    mod_b = tmp_path / "module_beta.py"
    mod_b.write_text("def beta(): return 2\n", encoding="utf-8")

    collided, _ = detect_tcas_collision(["module_alpha.py"], ["module_beta.py"], project_root=str(tmp_path))
    assert not collided

    # Case 3: Semantic AST collision (beta imports alpha)
    mod_b_imports_a = tmp_path / "module_beta_dep.py"
    mod_b_imports_a.write_text("import module_alpha\ndef beta(): return module_alpha.alpha()\n", encoding="utf-8")

    collided, reason = detect_tcas_collision(["module_alpha.py"], ["module_beta_dep.py"], project_root=str(tmp_path))
    assert collided
    assert "TCAS AST collision" in reason
    assert "module_alpha" in reason


def test_tcas_wave_separation(tmp_path: Path):
    """Verify _dot_som_nhat automatically separates colliding tasks into distinct waves."""
    mod_a = tmp_path / "producer.py"
    mod_a.write_text("def produce(): return 'data'\n", encoding="utf-8")

    mod_b = tmp_path / "consumer.py"
    mod_b.write_text("import producer\ndef consume(): return producer.produce()\n", encoding="utf-8")

    task_a = Task("T1.1", " ", "P1")
    task_a.vung_file = ["producer.py"]

    task_b = Task("T1.2", " ", "P1")
    task_b.vung_file = ["consumer.py"]

    tasks_theo_dot = {}
    wave_a = _dot_som_nhat(task_a, 1, tasks_theo_dot, project_root=str(tmp_path))
    assert wave_a == 1

    # Task B imports producer.py -> must be pushed to wave 2 despite no direct file overlap
    wave_b = _dot_som_nhat(task_b, 1, tasks_theo_dot, project_root=str(tmp_path))
    assert wave_b == 2
