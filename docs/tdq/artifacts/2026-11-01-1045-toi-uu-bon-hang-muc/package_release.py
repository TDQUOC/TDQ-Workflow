"""Validate the clean Git archive and create shareable release assets."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path.cwd()
E = Path(__file__).resolve().parent
OUT = Path.home() / ".codex/exports/tdq-workflow-v0.85.0"
OUT.mkdir(parents=True, exist_ok=True)
archive = OUT / "TDQ-Workflow-0.85.0.zip"
subprocess.run(["git", "archive", "--format=zip", "--prefix=TDQ-Workflow-0.85.0/", "--output", str(archive), "main"], check=True)
required = {"tdq_transcript", "tdq_test_result", "tdq_readiness", "tdq_runtime_bench", "tdq_test_manifest", "tdq_test_process", "tdq_test_receipt", "tdq_transcript_cache", "tdq_test_report", "tdq_test"}
with zipfile.ZipFile(archive) as package:
    prefix = "TDQ-Workflow-0.85.0/"
    files = [name[len(prefix):] for name in package.namelist() if not name.endswith("/")]
    assert len(files) == 169, len(files)
    assert not any(name.split("/")[0] in {"docs", "tests", "graphify-out", ".tdq-worktrees", ".git"} for name in files)
    versions = [json.loads(package.read(prefix + name))["version"] for name in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")]
    assert versions == ["0.85.0", "0.85.0"]
    for module in required:
        assert "scripts/" + module + ".py" in files, module
    compiled = 0
    for name in files:
        if name.endswith(".py"):
            compile(package.read(prefix + name), name, "exec")
            compiled += 1

original = ROOT / "docs/tdq/reports/2026-11-01-1045-toi-uu-bon-hang-muc-tom-tat.html"
summary = original.read_text(encoding="utf-8")
summary = summary.replace("Báo cáo ngày 01/11/2026", "Release v0.85.0 · 01/11/2026").replace("Triển khai &amp; QC: ĐẠT", "Full trước bump metadata: ĐẠT")
old = "<p><strong>Bàn giao:</strong> Chưa commit/push. Cổng đóng workflow còn bị chặn bởi 11 worktree cũ có thay đổi chưa commit; dữ liệu được giữ nguyên.</p>"
new = "<p><strong>Release v0.85.0:</strong> Đã commit và merge; gói phát hành từ nhánh main tinh gọn. Metadata workflow còn bị chặn bởi 11 worktree cũ; dữ liệu được giữ nguyên.</p><p><strong>Kiểm bổ sung:</strong> 60 test qua nhưng guard FAIL126 do cấu hình thay đổi; không tính là chứng nhận guard PASS mới. Xem release notes để biết phạm vi kiểm chứng.</p>"
assert old in summary
summary = summary.replace(old, new)
def remote_link(match):
    path = (original.parent / match.group(1)).resolve().relative_to(ROOT).as_posix()
    return 'href="https://github.com/TDQUOC/TDQ-Workflow/blob/dev/' + path + '"'
summary = re.sub(r'href="([^"]+)"', remote_link, summary)
html = OUT / "bao-cao-tom-tat-0.85.0.html"
html.write_text(summary, encoding="utf-8")
checksums = "".join(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name + "\n" for path in (archive, html))
(OUT / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
def commit(ref):
    return subprocess.check_output(["git", "rev-parse", ref], text=True).strip()
record = {"version": "0.85.0", "feature_commit": commit("9799793"), "dev_merge": commit("dev"), "main_release": commit("main"), "package": str(archive), "package_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "files": len(files), "python_files_compiled": compiled, "versions": versions, "required_runtime_modules": sorted(required), "forbidden_directories_absent": True, "validation_kind": "archive integrity and Python compilation, not Full/runtime recertification", "metadata_guard_verdict": "FAIL126 retained"}
(E / "release-package-validation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
