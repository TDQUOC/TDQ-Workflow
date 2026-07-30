# REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)

Ngày: 2026-07-29 · Spec: ../spec/2026-07-28-instruction-hardening-7b.md · Plan: ../plan/2026-07-28-instruction-hardening-7b.md · QC: ../qc/2026-07-28-instruction-hardening-7b.md

## Đã làm gì
- Hook sang vai **nhắc + kiểm bằng hiệu ứng thật**: 5 mã đóng (`TDQ:NEXT/APPROVE/LOG/STATE/GIT`), ledger `docs/tdq/.tdq-turn.jsonl` đối chiếu `remind` ↔ `observe`; không đọc transcript, không `deny`.
- Bỏ skill `tdq-approve`; duyệt bằng chat thường, state lưu nguyên văn câu user (`*_approved_by`).
- Gộp **10 → 6 skill**, thân skill dạng bước đánh số + `Xong khi:` + `Bước kế tiếp:`, chi tiết đẩy sang `references/`.
- `PHASE_TABLE` thành nguồn sự thật duy nhất; `phases.md` được **sinh** bằng `tdq_state.py phases-doc`, có test khoá đồng bộ.
- Thêm `scripts/doc_lint.py` (R1–R7) và test ngân sách token đo thật 8 mục của spec §2.7.
- Thêm bản **portable** cho agent ngoài Claude Code, có test chống lệch bước so với skills.

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| 6 skill mới | `skills/tdq-{intake,spec,plan,build,status,conventions}/` |
| Bản portable | `portable/AGENTS.md`, `portable/workflow/`, `portable/README.md` |
| Lint doc | `scripts/doc_lint.py` |
| CLI state | `scripts/tdq_state.py` (`next`, `phases-doc`, …) |
| Changelog + README 0.3.0 | `CHANGELOG.md`, `README.md` |
| Doc v0.1 lưu trữ | `docs/archive/v0.1/` |

## Cách chạy / cách kiểm
```
python3 -m unittest discover tests
python3 scripts/doc_lint.py skills portable
python3 scripts/tdq_state.py next
```

## Kết quả QC
PASS 15/15 hạng mục ở vòng 1 (162 test, `plugin validate --strict` PASS, smoke trên bản cài user-level 0.3.0). Chi tiết + bằng chứng: `docs/tdq/qc/2026-07-28-instruction-hardening-7b.md`.

## Quyết định đáng chú ý
- Kiểm tuân thủ bằng **hiệu ứng thật** thay vì tin dòng `✓` model in ra — model yếu rất hay in `✓` mà không làm.
- Doc phase **sinh từ code** thay vì viết tay — chặn đứng nguồn lệch phổ biến nhất.
- Bảng phase đặt ở `portable/workflow/phases.md` (spec ghi `AGENTS.md`); `AGENTS.md` trỏ tới, cùng một nguồn sinh.

## Giới hạn còn lại
- **RR7**: lint và test chỉ chứng minh doc đúng *hình dạng*; chưa có bằng chứng thực nghiệm rằng một model 7B chạy local đi đúng workflow. Muốn chắc phải chạy thử model thật — chưa làm trong phạm vi này.
- `~/.claude/CLAUDE.md` §10 **chưa** sửa: đang chờ user đọc bản mới và đồng ý (T7.2).
- Chưa commit — chờ user yêu cầu.
- Bản cài user-level đã lên 0.3.0 — **cần restart Claude Code** để hook/skill mới có hiệu lực.

## Ánh xạ tên skill cũ → mới
| Cũ | Mới |
|---|---|
| `tdq-start`, `tdq-analyze` | `tdq-intake` |
| `tdq-implement`, `tdq-qc`, `tdq-report` | `tdq-build` |
| `tdq-approve` | bỏ — duyệt bằng chat thường |
| `tdq-spec`, `tdq-plan`, `tdq-status`, `tdq-conventions` | giữ tên, viết lại |
