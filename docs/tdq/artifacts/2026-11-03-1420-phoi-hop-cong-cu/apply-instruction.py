"""Explicit approved user-level sync; run only after final regression passes."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
import tdq_setup

ART = Path(__file__).resolve().parent
TARGET = Path.home() / ".claude" / "CLAUDE.md"


def outside(data):
    start, end = tdq_setup.MOC_MO.encode(), tdq_setup.MOC_DONG.encode()
    assert data.count(start) == data.count(end) == 1
    before, rest = data.split(start, 1)
    _, after = rest.split(end, 1)
    return before + after


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    before = TARGET.read_bytes()
    acl = tdq_setup._acl_instruction(str(TARGET))
    mode = TARGET.stat().st_mode
    settings = json.loads((ART / "settings-apply-preflight.json").read_text(encoding="utf-8"))
    current = {name: digest(Path(name).read_bytes()) if Path(name).is_file() else None for name in settings}
    assert settings == current, "Settings changed since preflight; inspect before applying"
    backups = set(TARGET.parent.glob(TARGET.name + ".bak.*"))
    changed = tdq_setup.ghim_huong_dan_tool(str(TARGET), str(ROOT))
    after = TARGET.read_bytes()
    assert outside(before) == outside(after), "Private instruction bytes changed"
    created = set(TARGET.parent.glob(TARGET.name + ".bak.*")) - backups
    assert changed and len(created) == 1
    backup = created.pop()
    assert backup.read_bytes() == before
    assert tdq_setup._acl_instruction_bang_nhau(tdq_setup._acl_instruction(str(TARGET)), acl)
    assert tdq_setup._acl_instruction_bang_nhau(tdq_setup._acl_instruction(str(backup)), acl)
    assert TARGET.stat().st_mode == mode
    assert tdq_setup.ghim_huong_dan_tool(str(TARGET), str(ROOT)) is False
    assert TARGET.read_bytes() == after
    current = {name: digest(Path(name).read_bytes()) if Path(name).is_file() else None for name in settings}
    assert current == settings
    receipt = {"target": str(TARGET), "backup": str(backup), "backup_verified": True,
               "outside_before_sha256": digest(outside(before)),
               "outside_after_sha256": digest(outside(after)), "second_run_noop": True,
               "permissions_unchanged": True, "settings_unchanged": True,
               "before_sha256": digest(before), "after_sha256": digest(after)}
    (ART / "instruction-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
