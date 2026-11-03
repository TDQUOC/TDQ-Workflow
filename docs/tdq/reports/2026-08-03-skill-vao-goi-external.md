# REPORT — Đưa skill vào gói external (hybrid 3 nhánh)

Ngày: 2026-08-03 · Spec: ../spec/2026-08-03-skill-vao-goi-external.md · Plan: ../plan/2026-08-03-skill-vao-goi-external.md · QC: ../qc/2026-08-03-skill-vao-goi-external.md

## Đã làm gì
- Lệnh mới `skill-dump <tên>...`: chép NGUYÊN VĂN SKILL.md (bỏ frontmatter) + toàn bộ references, resolver 3 tầng (repo → `~/.claude/skills` → plugin), skill ma exit 1.
- `split-plan` nâng cấp: tách task nhãn `(mcp)` thành gói `"mcp": true` riêng (Claude tự làm), gói thường mang khóa `skills`; LUÔN chạy kể cả plan ≤6 task.
- `run-plan --plan-file <plan>`: máy-đối chiếu gói với khối `Dùng:` của plan — thiếu skill/leak mcp chỉ CẢNH BÁO (stderr + run.log), vẫn chạy engine.
- Khuôn AGENTS.md mới (fence 39 dòng ≤60) đặt ở root worktree, xóa trước diff-check/merge; khuôn gói thêm mục `## SKILL` cuối gói cho cả quick lẫn full.
- Cập nhật contract docs: tdq-build (nhánh external), 2 runner, tdq-plan + plan-template (luật nhãn `(mcp)`), tdq-intake (chặn quick external dùng MCP), portable 03/04.
- Log service hợp nhất 3 đường (skill-dump / split-plan / warning run-plan), tắt bằng `TDQ_EXTERNAL_LOG=0`.

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| skill-dump + split-plan mcp + check_packet_skills | `scripts/external_task.py` |
| Khuôn AGENTS.md | `skills/tdq-build/references/agents-md.md` |
| Khuôn gói có mục `## SKILL` | `skills/tdq-build/references/external-task.md` |
| Nhánh external + runner | `skills/tdq-build/SKILL.md`, `agents/{codex,agy}-runner.md` |
| Luật nhãn `(mcp)` | `skills/tdq-plan/SKILL.md` + `references/plan-template.md`, `skills/tdq-intake/SKILL.md` |
| Portable sync | `portable/workflow/03-plan.md`, `04-build.md` |
| Test mới | `tests/test_skill_docs.py` (mới) + 8 class trong `tests/test_external_task.py` |

## Cách chạy / cách kiểm
```
cd tests && python3 -m unittest            # toàn suite
python3 scripts/external_task.py skill-dump <tên-skill>
python3 scripts/external_task.py run-plan ... --plan-file <plan>
```

## Kết quả QC
9/9 hạng mục (Q1–Q9) PASS vòng 1 — suite `Ran 439 tests ... OK` (401→439), doc_lint spec + `--pair` exit 0, graphify exit 0. Bằng chứng: ../qc/2026-08-03-skill-vao-goi-external.md.

## Quyết định đáng chú ý
- Chép nguyên văn skill thay vì trích đoạn — vì model cấp thấp không được phép tự tóm tắt/suy diễn (user chốt).
- Enforcement = warning trong script, không hard-block — vì thiếu skill trong gói không chắc là lỗi chết người; log đủ để truy.
- Task cần MCP tool tách khỏi gói external bằng nhãn máy-đọc `(mcp)` ngay từ bước lập plan.

## Giới hạn còn lại
- Chưa chạy end-to-end với engine thật (codex/agy) — QC dùng stub engine; lần external kế tiếp là lượt kiểm thực tế.
- `check_packet_skills` so khớp header nguyên văn, không kiểm nội dung skill dán vào có đủ/đúng.

## Đề xuất tiếp theo
- Lần chạy external thật đầu tiên: xem `run.log` xác nhận warning-path im lặng khi gói đủ skill.
