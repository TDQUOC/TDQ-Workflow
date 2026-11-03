# QC — TDQ workflow là default tuyệt đối + bỏ mục superpower

Ngày: 2026-08-02 · Spec: ../spec/2026-08-02-tdq-default-cleanup.md (1.1) · Plan: ../plan/2026-08-02-tdq-default-cleanup.md

## Backup CLAUDE.md (T2.1)
- File: `docs/tdq/qc/claude-md-backup-2026-08-02.bak` — copy byte-nguyên `~/.claude/CLAUDE.md` trước khi sửa.
- Ngày backup: 2026-08-02 · Lý do: `~/.claude/CLAUDE.md` nằm ngoài repo, không có git rollback.
- sha256 bản gốc: `f19af36608323f4aa403679bd3f1515491ec0e6b1df6e8dd35b7af76cbdaa3a4`
- `diff .bak ~/.claude/CLAUDE.md` exit 0 đã chạy 1 lần TRƯỚC khi sửa (đúng luật T2.1).

## Bảng QC Q1–Q6

| # | Hạng mục | Lệnh | Output thật | Kết quả |
|---|---|---|---|---|
| Q1 | Toàn suite | `python3 -m unittest discover -s tests` | `Ran 371 tests in 35.788s` / `OK` (có 4 test mới tests/test_prompt_context.py) | PASS |
| Q2 | Lint docs | `doc_lint.py skills/tdq-intake/SKILL.md` và `doc_lint.py --pair spec plan` | cả hai exit 0 | PASS |
| Q3 | Sạch superpower | `grep -ci superpower ~/.claude/CLAUDE.md` | `0` | PASS |
| Q4 | Luật MỌI prompt | `grep -c "MỌI prompt mới" ~/.claude/CLAUDE.md` = 1; `head -4 SKILL.md \| grep -c "kể cả câu hỏi"` = 1 | cả hai khớp | PASS |
| Q5 | Hook chạy thật 4 case | echo payload → `prompt_context.py` (fixtures scratchpad t13) | none/noactive: chỉ `[TDQ:INTAKE]`; idle: `[TDQ:INTAKE]` + `[TDQ:NEXT] … phase idle` (INTAKE nguyên vẹn, đứng đầu); open (phase spec): chỉ `[TDQ:NEXT]`, KHÔNG có INTAKE | PASS |
| Q6 | Tham chiếu cũ + đánh số | grep scope đóng T2.4 = 0 dòng (đã sửa knowledge + title spec); `grep -E '^## [0-9]+\.'` = dãy 1,2,…,10 liên tục | 0 và 1..10 | PASS |

## QC vòng 1 — 5 fail phát hiện ở T4.1, đã fix (QC1.1–QC1.3)
- Hook so phase THÔ nên lane quick đang chạy (phase=idle thô) bị bắn INTAKE nhầm, nuốt APPROVE → fix dùng `tdq_state.phase_key(state)`.
- 2 test cũ theo hợp đồng cũ (im lặng khi no state; quick approved 1 dòng) → cập nhật theo hợp đồng mới (INTAKE xuất hiện, quick đóng = INTAKE+NEXT).
- Tổng description skill 956/911 > 900 → rút gọn description tdq-intake, vẫn giữ "kể cả câu hỏi". Kết quả: suite 371 OK.
- Ghi chú: title spec sửa sau duyệt (bỏ chuỗi "§5 superpower" theo test T2.4) → đã refresh sha qua `tdq_state.py set spec_file=…`, nội dung spec không đổi.

## Đối chiếu §5 superpower (cũ) → chỗ thay thế trong plugin

| Ý trong §5 cũ | Thay thế |
|---|---|
| Hỏi user có muốn codex/antigravity thực thi + report file mỗi task | tdq-plan bước 1 (mode external) + tdq-build "Nhánh external" (report JSON mỗi task) |
| Tick status vào plan khi doing/done | tdq-build luật "Tick ngay" + CLAUDE.md §9 "Tick [x] NGAY khi pass" |
| Implement end-to-end 1 turn, không dừng giữa chừng | tdq-build "End-to-end trong MỘT turn" + CLAUDE.md §9 |
| Chờ sub-agent hoặc đặt trigger tự tiếp tục | tdq-build "Chờ subagent thì chờ hết" |
| Spec/plan tiếng Việt | tdq-spec/tdq-plan ("viết tiếng Việt") + CLAUDE.md §9 |
| Spec và plan không cùng turn; tóm tắt spec chờ duyệt | tdq-spec bước 4 + CLAUDE.md §9 "Spec và plan không lập trong cùng một turn" |
| Hỏi commit sau khi xong + test ổn | tdq-build Phần C bước 10 (hỏi commit, cấm tự commit) |

Kết luận: mọi ý §5 đều có chỗ thay thế — xóa trọn không làm tụt chuẩn.
