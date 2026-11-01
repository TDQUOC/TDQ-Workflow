"""Hook test fixtures must not inherit another project's state anchor."""
import os
from unittest.mock import patch

from helper import load_fixture, run_hook, tdq_state, write_state


def test_payload_fixture_overrides_inherited_project(tmp_path, monkeypatch):
    foreign = tmp_path / "foreign"
    fixture = tmp_path / "fixture"
    write_state(str(foreign), active_request="foreign", phase="spec")
    write_state(str(fixture), active_request=None, phase="idle")
    before = {p.relative_to(foreign): p.read_bytes()
              for p in foreign.rglob("*") if p.is_file()}
    monkeypatch.setenv("TDQ_PROJECT_DIR", str(foreign))
    payload = load_fixture("prompt.json", cwd=str(fixture), session_id="scope")

    code, output, error = run_hook("prompt_context.py", payload)

    assert code == 0, error
    assert "[TDQ:INTAKE]" in output
    assert "[TDQ:NEXT]" not in output
    assert any(row["kind"] == "turn_start"
               for row in tdq_state.turn_log_read(str(fixture), session="scope"))
    assert before == {p.relative_to(foreign): p.read_bytes()
                      for p in foreign.rglob("*") if p.is_file()}
    assert os.environ["TDQ_PROJECT_DIR"] == str(foreign)


def test_explicit_project_override_still_wins(tmp_path, monkeypatch):
    inherited = tmp_path / "inherited"
    fixture = tmp_path / "fixture"
    selected = tmp_path / "selected"
    for project in (inherited, fixture, selected):
        write_state(str(project), active_request=None, phase="idle")
    before = {str(p): p.read_bytes() for project in (inherited, fixture)
              for p in project.rglob("*") if p.is_file()}
    monkeypatch.setenv("TDQ_PROJECT_DIR", str(inherited))
    payload = load_fixture("prompt.json", cwd=str(fixture), session_id="scope")

    code, _, error = run_hook(
        "prompt_context.py", payload, env={"TDQ_PROJECT_DIR": str(selected)})

    assert code == 0, error
    assert any(row["kind"] == "turn_start"
               for row in tdq_state.turn_log_read(str(selected), session="scope"))
    assert before == {str(p): p.read_bytes() for project in (inherited, fixture)
                      for p in project.rglob("*") if p.is_file()}
    assert os.environ["TDQ_PROJECT_DIR"] == str(inherited)


def test_fixture_scope_preserves_safety_flags(tmp_path, monkeypatch):
    monkeypatch.setenv("TDQ_PROJECT_DIR", "foreign")
    monkeypatch.setenv("TDQ_KHONG_CHAM_MAY", "1")
    with patch("helper.subprocess.run") as child:
        child.return_value.returncode = 0
        child.return_value.stdout = child.return_value.stderr = ""
        run_hook("prompt_context.py", {"cwd": str(tmp_path)})
    environment = child.call_args.kwargs["env"]
    assert environment["TDQ_PROJECT_DIR"] == str(tmp_path)
    assert environment["TDQ_KHOI_TAO_NEN"] == "0"
    assert environment["TDQ_KHONG_CHAM_MAY"] == "1"


def test_malformed_payload_is_still_sent_to_hook(monkeypatch):
    monkeypatch.setenv("TDQ_PROJECT_DIR", "foreign")
    with patch("helper.subprocess.run") as child:
        child.return_value.returncode = 0
        child.return_value.stdout = child.return_value.stderr = ""
        run_hook("prompt_context.py", ["invalid"])
    assert child.call_args.kwargs["input"] == '["invalid"]'
    assert child.call_args.kwargs["env"]["TDQ_PROJECT_DIR"] == "foreign"


def test_payload_subdirectory_resolves_fixture_root(tmp_path, monkeypatch):
    write_state(str(tmp_path), active_request=None, phase="idle")
    nested = tmp_path / "src"
    nested.mkdir()
    monkeypatch.setenv("TDQ_PROJECT_DIR", "foreign")
    with patch("helper.subprocess.run") as child:
        child.return_value.returncode = 0
        child.return_value.stdout = child.return_value.stderr = ""
        run_hook("prompt_context.py", {"cwd": str(nested)})
    assert child.call_args.kwargs["env"]["TDQ_PROJECT_DIR"] == str(tmp_path)
