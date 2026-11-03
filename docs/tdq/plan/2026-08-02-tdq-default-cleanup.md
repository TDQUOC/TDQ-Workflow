# PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower

Ngày: 2026-08-02 · Spec: ../spec/2026-08-02-tdq-default-cleanup.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — plan nhỏ, đụng file ngoài repo (~/.claude/CLAUDE.md) cần backup cẩn thận, task phụ thuộc chặt.
Trạng thái plan: HOÀN THÀNH

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| doc_lint (script) | T3.3 | lint SKILL.md intake + `--pair` spec/plan exit 0 |
| unittest suite | T1.1, T4.1 | tests/test_prompt_context.py mới pass + toàn suite pass |
| tavily-search | T0 (đã xong ở analyze) | docs/tdq/research/2026-08-02-tdq-default-cleanup.md đã tồn tại |
| graphify | T4.3 | graph rebuild sau khi code đổi, graphify-out/ cập nhật |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P0 — Nền (đã xong ở analyze)
- [x] **T0** Research 2 truy vấn hook/description qua tavily-search — Test: file research/2026-08-02-tdq-default-cleanup.md tồn tại, có nguồn.
  - Dùng: `tavily-search`
  - Nạp: đã gọi tool `tavily-primary` ở phase analyze; task này chỉ ghi nhận, không gọi thêm.
  - Để: căn cứ thiết kế 3 tầng (hook deterministic vs instruction xác suất).
  - Ra: docs/tdq/research/2026-08-02-tdq-default-cleanup.md
  - Kiểm: `test -s docs/tdq/research/2026-08-02-tdq-default-cleanup.md`
  - Không dùng cho: research thêm trong build — không cần, tránh phí quota.

## P1 — Hook [TDQ:INTAKE] (red → green)
- [x] **T1.1** Viết tests/test_prompt_context.py với 4 case: (a) state None → chỉ [TDQ:INTAKE]; (b) có state nhưng thiếu active_request → chỉ [TDQ:INTAKE]; (c) phase idle còn active_request → [TDQ:NEXT] + [TDQ:INTAKE], tổng output ≤ MAX_CHARS và dòng INTAKE nguyên vẹn không bị _truncate cắt; (d) phase spec (request mở) → KHÔNG có [TDQ:INTAKE]; kèm assert dòng INTAKE ≤160 ký tự — Test: `python3 -m unittest tests.test_prompt_context` — red: case a–c fail (case d không ràng); green sau T1.2: 4/4 pass.
  - Dùng: `unittest suite`
  - Nạp: theo khuôn test hook hiện có trong tests/ (subprocess echo payload JSON vào hooks/scripts/prompt_context.py, TDQ_PROJECT_DIR trỏ thư mục tạm).
  - Để: chốt hợp đồng 4 case + trần 160 ký tự trước khi sửa code.
  - Ra: tests/test_prompt_context.py
  - Kiểm: `python3 -m unittest tests.test_prompt_context` (đỏ trước T1.2, xanh sau T1.2)
  - Không dùng cho: test stop_gate hay tdq_state — ngoài phạm vi.
- [x] **T1.2** Sửa hooks/scripts/prompt_context.py: nhánh state None / thiếu active_request in chỉ [TDQ:INTAKE]; phase idle in [TDQ:NEXT] + [TDQ:INTAKE]; wording "chưa có request mở — nếu prompt KHÔNG thuộc vòng intake đang dở thì mở tdq-intake trước khi làm gì khác", ≤160 ký tự — Test: `python3 -m unittest tests.test_prompt_context` xanh 4/4.
- [x] **T1.3** Chạy tay hook 4 case bằng echo payload thật (state None; state thiếu active_request; phase idle; phase spec) — Test: output đúng kỳ vọng Q5 của spec cho cả 4 case, dán bằng chứng vào file QC.

## P2 — CLAUDE.md user-level
- [x] **T2.1** Backup nguyên văn ~/.claude/CLAUDE.md ra file riêng docs/tdq/qc/claude-md-backup-2026-08-02.bak (copy byte-nguyên, ghi chú ngày+lý do đặt ở file QC, KHÔNG ghi vào .bak); lưu sha256 của bản gốc vào file QC — Test (chạy đúng 1 lần, TRƯỚC T2.2): `diff docs/tdq/qc/claude-md-backup-2026-08-02.bak ~/.claude/CLAUDE.md` exit 0; sau T2.2 chỉ kiểm sha256 file .bak khớp giá trị đã lưu.
- [x] **T2.2** Xóa §5 superpower, đánh số lại mục 6–11 → 5–10 theo mapping §1b của spec — Test: `grep -ci superpower ~/.claude/CLAUDE.md` = 0 và dãy `^## <n>.` là 1..10 liên tục.
- [x] **T2.3** Viết lại đầu mục TDQ (số mới 9): "MỌI prompt mới → tdq-intake, kể cả câu hỏi thuần giải đáp/check/việc nhỏ; message trong luồng request đang mở không tính" — Test: `grep -c "MỌI prompt mới" ~/.claude/CLAUDE.md` ≥ 1.
- [x] **T2.4** Quét sửa tham chiếu số mục cũ trong file đang sống — scope đóng: ~/.claude/CLAUDE.md, skills/, portable/, hooks/, docs/tdq/{knowledge,spec}/2026-08-02-* — Test: cả hai lệnh ra 0 dòng: `grep -rn 'CLAUDE.md §10\|CLAUDE.md mục 10\|§5 superpower\|mục 5 .superpower' skills/ portable/ hooks/ docs/tdq/knowledge/2026-08-02-tdq-default-cleanup.md docs/tdq/spec/2026-08-02-tdq-default-cleanup.md` và `grep -n '§10\|§11\|mục 10\|mục 11' ~/.claude/CLAUDE.md`.

## P3 — Skill tdq-intake
- [x] **T3.1** Sửa description frontmatter SKILL.md intake: thêm "Dùng cho MỌI prompt mới, kể cả câu hỏi/giải đáp/check nhỏ" — Test: grep "kể cả câu hỏi" trong 4 dòng đầu skills/tdq-intake/SKILL.md ra 1 dòng.
- [x] **T3.2** Thêm vào mở đầu Phần A của SKILL.md intake: định nghĩa "yêu cầu mới" (mọi prompt khi không có request mở; phase ≠ idle thì message thuộc request đang chạy) — Test: grep "request mở" skills/tdq-intake/SKILL.md ≥ 1.
- [x] **T3.3** Lint docs sau sửa — Test: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md` exit 0 và `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-02-tdq-default-cleanup.md docs/tdq/plan/2026-08-02-tdq-default-cleanup.md` exit 0.
  - Dùng: `doc_lint (script)`
  - Nạp: chạy scripts/doc_lint.py trực tiếp, không cần nạp skill.
  - Để: bảo đảm SKILL.md sửa xong vẫn đạt chuẩn R1–R8 và spec/plan khớp nhau.
  - Ra: output lint exit 0 (dán vào QC).
  - Kiểm: hai lệnh ở dòng Test exit 0.
  - Không dùng cho: lint file docs lịch sử của request cũ.

## P4 — QC & đóng
- [x] **T4.1** Toàn suite — Test: `python3 -m unittest discover -s tests` OK 0 fail.
  - Dùng: `unittest suite`
  - Nạp: chạy từ repo root bằng dạng discover.
  - Để: chứng minh không hỏng gì ngoài phạm vi (Q1).
  - Ra: dòng tổng "Ran N tests ... OK" dán vào file QC.
  - Kiểm: exit 0, 0 fail.
  - Không dùng cho: đo hiệu năng.
- [x] **T4.2** Điền bảng QC Q1–Q6 + đối chiếu §5→plugin vào docs/tdq/qc/2026-08-02-tdq-default-cleanup.md — Test: file có đủ 6 hàng PASS kèm lệnh + output thật, có bảng đối chiếu từng ý §5 → chỗ thay thế trong plugin.
- [x] **T4.3** Graph rebuild + working log + report — Test: `graphify extract . --code-only` chạy xong; working log có entry build; report ≤50 dòng tại docs/tdq/reports/2026-08-02-tdq-default-cleanup.md, doc_lint exit 0.
  - Dùng: `graphify`
  - Nạp: chạy CLI `graphify extract . --code-only` cuối turn build (không cần nạp skill).
  - Để: cập nhật code graph sau khi hook/tests đổi (quy ước mục TDQ của CLAUDE.md).
  - Ra: graphify-out/ cập nhật (mtime mới).
  - Kiểm: lệnh exit 0.
  - Không dùng cho: trả lời câu hỏi kiến trúc trong build này.

## QC vòng 1 — fix
- [x] **QC1.1** Hook dùng `tdq_state.phase_key(state)` thay vì phase thô để phán "request mở" (lane quick giữ phase=idle thô khi đang chạy → INTAKE bắn nhầm, nuốt APPROVE) — Test: 3 test quick trong test_context_hooks + test_e2e_chain pass, 4 test test_prompt_context vẫn pass.
- [x] **QC1.2** Cập nhật test_no_request_silent theo hợp đồng mới (không state → in [TDQ:INTAKE]) — Test: test đó pass.
- [x] **QC1.3** Rút gọn description tdq-intake để tổng description ≤900 ký tự, vẫn giữ cụm "kể cả câu hỏi" trong frontmatter — Test: test_skill_descriptions_total pass + grep T3.1 vẫn 1 dòng.

## Definition of Done
Trỏ §6 spec (bản 1.1): Q1 toàn suite OK có test mới · Q2 lint + pair exit 0 · Q3 grep superpower = 0 · Q4 luật "MỌI prompt mới" ở cả CLAUDE.md và frontmatter intake · Q5 hook chạy thật đúng 3 kỳ vọng theo case · Q6 tham chiếu cũ = 0 + dãy mục 1..10 liên tục. Working log ghi đủ.
