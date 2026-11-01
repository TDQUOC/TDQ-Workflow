"""Read-only verification and documentation bookkeeping; no test execution."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def bind(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

index = load(E / "evidence-index.json")
index["checks"]["Q7"]["qc"] = bind(E / "independent-qc.json")
reports = []
for role, prefix, browser in (("slow-tests", "slow-tests", "slow-tests-browser.json"), ("request", "request-report", "request-browser.json")):
    reports.append({"role": role, "html": bind(E / (prefix + ".html")), "markdown": bind(E / (prefix + ".md")), "source": bind(E / "final-result.json"), "browser": bind(E / browser), "numbers": [{"source": bind(E / "final-result.json"), "pointer": "/tests_run"}, {"source": bind(E / "final-result.json"), "pointer": "/skipped"}] if role == "request" else [{"source": bind(E / "slow-tests.json"), "pointer": "/case_count"}, {"source": bind(E / "slow-tests.json"), "pointer": "/execution_phase_seconds"}]})
index["checks"]["Q8"]["reports"] = reports
save(E / "evidence-index.json", index)
checks = []
for number in range(1, 9):
    command = [sys.executable, str(E / "verify_scope.py"), "Q" + str(number)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
    row = {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    checks.append(row)
    print(result.stdout.strip())
save(E / "qc-checks.json", checks)
if any(row["exit_code"] for row in checks):
    raise SystemExit(1)

full = load(E / "final-result.json")
skips = [row for row in full["case_outcomes"] if row.get("outcome") == "skip"]
save(E / "final-skips.json", skips)
sources = [ROOT / "scripts" / name for name in ("tdq_bench.py", "tdq_codex.py", "tdq_test.py", "tdq_test_process.py", "tdq_test_report.py")]
imports = {}
for path in sources:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [item.name for item in node.names]
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    assert not any(name.split(".")[0] in {"tests", "hooks"} for name in modules)
    imports[path.relative_to(ROOT).as_posix()] = modules
constraints = {
    "scripts_do_not_import_hooks": {"status": "PASS", "method": "AST all imports in five touched production modules", "imports": imports},
    "state_single_writer": {"status": "PASS", "method": "Reviewed final diff and write sites; runner writes test result/cache, renderer only export bundle; no new state writer. Existing bench temporary-project state uses tdq_state.save."},
    "production_does_not_import_tests": {"status": "PASS", "method": "Same AST import inventory; real CLI regression and Full architectural tests passed."},
    "new_code_module_location": {"status": "PASS", "path": "scripts/tdq_test_report.py"},
}
save(E / "architecture-constraints.json", constraints)
clean = {
    "SRP": "CÓ — pure summary/render tách khỏi export I/O; OwnedProcessJob sở hữu lifecycle, Codex giữ probe policy; lỗi purity đã sửa tại owner T1.3.",
    "OCP": "CÓ — phase/ranking/format và validation sets dùng dữ liệu, không thêm abstraction một use case; primitive có hai consumer Codex/IsolatedJob thực.",
    "LSP": "CÓ — IsolatedJob giữ hợp đồng OwnedProcessJob và thêm pytest isolation; regression giữ caller env/HOME, stdin và error contracts; summary trả cùng schema quality.",
    "ISP": "CÓ — summary chỉ nhận result, renderer nhận summary/provenance; process chỉ nhận launch/ownership inputs cần dùng.",
    "DIP": "CÓ — Codex/pytest đi qua OwnedProcessJob, summary/export dùng tdq_test_report; state vẫn qua shared tdq_state; không nhân bản backend process.",
}
save(E / "clean-code-check.json", clean)
qc = ROOT / "docs/tdq/qc" / (E.name + ".md")
qc.parent.mkdir(exist_ok=True)
lines = ["# QC — Tối ưu bốn hạng mục", "", "Ngày: 2026-11-01 · Lane full · QC ultra · Source " + load(E / "runtime.json")["source_sha256"], "Soul: chất lượng > runtime > context cost", "", "| # | Lệnh / chứng cứ | Kết quả |", "|---|---|---|"]
for row in checks:
    value = json.loads(row["stdout"])
    lines.append(f'| {value["check"]} | verify_scope.py {value["check"]} · qc-checks.json | PASS |')
lines += ["| QC-F1 | Full --workers 1 --fresh --reuse off; QC-F1-check.json, test-budget-final.json | PASS: 3657 pass / 8 skip; 1 Full / budget2; 0 radius miss |", "| QC-F2 | Guarded parent/radius T1.1, T1.2, T2.1, T3.1-owner, T3.2 và Full cuối | PASS: phủ tất cả Chạm, không chạy lặp cùng suite |", "| QC-F3 | architecture-constraints.json, AST + final diff + architectural Full cases | PASS: 4 ràng buộc |", "| QC-F4 | clean-code-check.json + independent-qc.md | PASS: 5 câu trả lời có và các owner fix đã kiểm |", "", "## Bằng chứng lệnh Q1–Q8", ""]
for row in checks:
    lines += ["```json", row["stdout"].strip(), "```", ""]
lines += ["## Clean code", ""] + [f"- {key}: {value}" for key, value in clean.items()]
lines += ["", "## Giới hạn và trạng thái", "", "Các 8 skip có ID/reason raw trong final-skips.json và result gốc; không biến thành PASS. D9/D10 SKIPPED_USER; không chứng nhận hiệu năng A/B, POSIX, thiết bị vật lý. Receipt FAIL trung gian được giữ. Ngoại lệ telemetry giới hạn đúng appendix đã duyệt. Browser thực direct CDP khi MCP Transport closed; đủ hai role × hai viewport, không phải MCP/physical device. LSP final check server process exited; trước triển khai đã có references/blast radius, cuối chỉ đọc source và dùng AST/grep; graph freshness được cập nhật ở tdq_finish, không là chứng cứ correctness thay test.", "", "## Lệch spec chờ duyệt", "", "tdq_state.py lech list: 0 item(s), 0 pending. Không nới ngưỡng DoD.", "", "## Kết luận", "", "PASS 12/12 mục chất lượng (Q1–Q8 và QC-F1–F4). Workflow chưa đóng: phase=implement vì guard11worktree cũ dirty; không sửa guard/ledger hoặc xóa source cũ. Chưa commit/push phần mới.", ""]
qc.write_text("\n".join(lines), encoding="utf-8")
plan = ROOT / "docs/tdq/plan" / (E.name + ".md")
text = plan.read_text(encoding="utf-8")
for task in ("T4.3", "T5.1", "T5.2"):
    text = text.replace(f"- [~] **{task}**", f"- [x] **{task}**").replace(f"- [ ] **{task}**", f"- [x] **{task}**")
for number in range(1, 9):
    text = text.replace(f"- [ ] Q{number} ", f"- [x] Q{number} ")
text = text.replace("Trạng thái plan: ĐÃ DUYỆT —", "Trạng thái plan: HOÀN THÀNH THỰC THI/QC — workflow chưa đóng do worktree cũ; ")
text += "\nT4.3/T5.1/T5.2 và Q1–Q8 đã parent verifier PASS đúng sourceFull; QC12/12. Browser trực tiếp Chrome CDP khi MCP Transportclosed, đủ4capture/DOM/console/interaction, không phải physicaldevice. Workflow phaseimplement vẫn blocked11foreignWT; chưacommit/push, không bỏguard hoặcđánhledgerclosedgiả.\n"
plan.write_text(text, encoding="utf-8")
save(E / "completion-checkpoint.json", {"technical_status": "PASS", "checks": 12, "workflow_status": "BLOCKED_BY_FOREIGN_DIRTY_WORKTREES", "phase": "implement", "source_sha256": load(E / "runtime.json")["source_sha256"], "qc": bind(qc), "plan": bind(plan), "commit_created": False, "push_performed": False})
print("Documentation complete; workflow gate remains blocked and unchanged.")
