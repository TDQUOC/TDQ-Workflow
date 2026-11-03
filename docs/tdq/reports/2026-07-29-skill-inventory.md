# REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)

Ngày: 2026-07-29 · Spec: ../spec/2026-07-29-skill-inventory.md (1.1) · Plan/QC: cùng slug

## Vấn đề
Workflow không hề rà soát skill phụ trợ đang có — điểm mù, không phải giới hạn kỹ thuật.
Đo thật: đĩa 7 skill, context 18 (built-in không nằm trên đĩa); quét ẩu cache ra 152 file
rác. User chốt: đã `DÙNG` thì plan phải quy rõ dùng thế nào, không "implement mù".

## Đã làm gì

- **`scripts/skill_inventory.py`**: quét đúng 3 nguồn (user / project / plugin đang bật —
  gộp `enabledPlugins` 3 tầng, chỉ đọc `installPath`, bỏ `scope: project` của project khác,
  cấm quét cache); luôn in 2 dòng nhắc chép built-in; lọc ký tự điều khiển; log qua `TDQ_LOG`.
- **Bước B0 ở intake** (+ checklist `analyze`/`quick` trong PHASE_TABLE): điền bảng phán
  quyết vào `knowledge/<slug>.md`. Quy tắc "1%" mã hoá thành: xét 100% bắt buộc · loại chỉ
  bằng 4 lý do đóng · **phân vân → DÙNG**. Lane quick: 1 dòng `Năng lực:` trong mini-plan.
- **Spec §3b** (phán quyết `DÙNG/KHÔNG/NỀN`) → **hợp đồng 6 trường trong plan**
  (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`) → **build nạp skill trước bước đỏ** → **QC chạy
  trường `Kiểm` thật**. Máy cưỡng chế: `doc_lint` R8 + `doc_lint --pair <spec> <plan>`.
- Portable: agent ngoài xét công cụ tương đương như skill, dòng `DÙNG` ghi `tương đương:`.

## Đầu ra

| Đầu ra | Đường dẫn |
|---|---|
| Script + test | `scripts/skill_inventory.py` · `tests/test_skill_inventory.py` (11 test) |
| Intake B0 | `skills/tdq-intake/SKILL.md` · `references/skill-inventory.md` |
| Khuôn | `spec-template.md` (§3b) · `plan-template.md` (bảng + khối 6 trường) |
| Lint | `scripts/doc_lint.py` (R8, `--pair`) · `tests/test_doc_lint.py` (+12 test) |
| Build/QC | `skills/tdq-build/SKILL.md` · `references/qc.md` mục 6 |
| Đồng bộ | `PHASE_TABLE` + `phases.md` ×2 · `portable/` · 4 spec cũ miễn trừ R8 |
| Đóng gói | `CHANGELOG.md` 0.3.3 · `plugin.json` 0.3.3 · cài lại user-level |

## Kết quả QC

**Ran 227 tests, OK** (0.3.2: 204) · `doc_lint skills portable docs/tdq/spec` exit 0 ·
`--pair` dogfood trên chính cặp spec/plan này exit 0 · `plugin validate --strict` PASS ·
**14/14 PASS** vòng 1 sau 2 fix: **QC1.1** (Q9 — ANSI escape từ SKILL.md xấu lọt ra terminal
→ lọc ký tự < 0x20, red→green) và **Q10** (khuôn copy chứa ví dụ thật → placeholder).

## Lệch so với spec (chi tiết + lý do ở file QC)

Thêm phán quyết `NỀN` cho skill khung (tránh hardcode ngoại lệ tdq-* trong lint) · mục quick
vào key `quick` thay vì `no_state` · spec dir chỉ chịu R8 · Q9 rà thủ công đúng phạm vi hợp
đồng vì skill `security-review` fail nạp (repo không có remote).

## Còn chờ user

Commit (0.3.0→0.3.3) · restart Claude Code · state vẫn trỏ request cũ (`init` sẽ xoá).
