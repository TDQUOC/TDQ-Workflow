# MINI-PLAN — Thực thi 5 task P0 tối ưu token

Ngày: 2026-08-04 · Lane quick · Request: ../requests/2026-08-04-thuc-thi-p0-token.md
Nguồn đề xuất: ../knowledge/2026-08-04-de-xuat-toi-uu-token.md · Trạng thái: ĐÃ DUYỆT (quick) · XONG 8/8 task

## Chốt từ interview

- A5 gốc đã có sẵn → thay bằng **luật lint đúng file, cấm lint cả thư mục** (nguồn thật của 2,6M).
- Luật prose D1/D2 ghi vào **skill plugin**, KHÔNG động `~/.claude/CLAUDE.md` (giữ nhất quán với C1).
- B1 dùng **`search-scout`** (đã gọi được Tavily MCP). B2/Explore để đợt sau.
- C1 (CLAUDE.md bản lõi) NGOÀI phạm vi đợt này — là hạng P1, cần chuyển nội dung sang skill trước.

Năng lực: không có (việc thuần nội bộ, không cần MCP/web).

## Task

- [x] **1 — A4a** `scripts/tdq_state.py`: `init`/`set`/`reset` mặc định in 1 dòng
  `✅ <cmd>: request=<slug> lane=<lane> phase=<phase>`; thêm cờ `--json` in nguyên state như cũ.
  Test: `tests/test_state.py` — không cờ → output ≤1 dòng và không chứa `{`; có `--json` → parse được JSON.
- [x] **2 — A4b** `next` mặc định giữ nguyên (hook đã dùng `--brief`); chỉ thêm 1 dòng ghi chú
  trong `skills/tdq-status/SKILL.md`: Claude gọi `next --brief` trừ khi thật sự cần checklist đầy đủ.
  Test: `tests/test_skill_docs.py` — file có chuỗi `next --brief`.
- [x] **3 — A5′** Luật lint: `skills/tdq-conventions/SKILL.md` thêm "chạy `doc_lint.py` trên ĐÚNG file
  vừa sửa, cấm truyền thư mục". Sửa mọi chỗ trong skill/portable còn dạy lint thư mục.
  Test: `tests/test_skill_docs.py` — `grep -c 'doc_lint.py docs/tdq$'` trong skills = 0.
- [x] **4 — D1** `skills/tdq-conventions/SKILL.md` thêm luật gộp lệnh Bash: 2–5 lệnh độc lập đã biết
  trước thì gộp 1 call bằng `&&`; tách lại khi có lệnh fail.
  Test: `tests/test_skill_docs.py` — file chứa `gộp` + `&&`.
- [x] **5 — D2** `skills/tdq-build/SKILL.md`: lúc implement chỉ chạy test của module đang sửa;
  full suite chạy ĐÚNG 1 lần ở QC. Sửa dòng 47 và mục QC cho khớp.
  Test: `tests/test_skill_docs.py` — có `test của module` và `full suite` chỉ gắn với QC.
- [x] **6 — B1** `skills/tdq-intake/SKILL.md` bước 3 (Research): mặc định giao `search-scout`,
  agent tự ghi `docs/tdq/research/<slug>.md`, trả về digest **≤1.500 ký tự**. Ngoại lệ: ≤1 truy vấn
  thì Claude tự làm. Test: `tests/test_skill_docs.py` — có `search-scout` và `1.500 ký tự`.
- [x] **7** Đồng bộ `portable/workflow/*.md` cho khớp skill (ràng buộc `test_portable_sync`),
  chạy `doc_lint` trên đúng file đã sửa. Test: `cd tests && python3 -m unittest test_portable_sync` OK.
- [x] **8** Full suite ĐÚNG 1 lần + đo lại `python3 scripts/token_audit.py --sessions 2`,
  ghi số trước/sau vào working log. Test: `Ran … OK`, exit 0.

## Validate cuối

`cd tests && python3 -m unittest discover -s . -p "test_*.py"` → OK (chạy 1 lần duy nhất).
Không commit/push trừ khi user yêu cầu. Không sửa `~/.claude/CLAUDE.md`.

## Rủi ro

- Đổi output `tdq_state.py` có thể vỡ test/hook đang assert JSON → task 1 phải chạy
  `test_state.py`, `test_next.py`, `test_stop_gate.py`, `test_context_hooks.py` trước khi đi tiếp.
- `test_portable_sync.test_steps_match_skills` so bước skill ↔ portable → task 7 bắt buộc.
