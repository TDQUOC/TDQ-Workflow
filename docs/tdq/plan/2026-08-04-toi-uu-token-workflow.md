# PLAN — Đề xuất tối ưu time/token cho TDQ workflow

Ngày: 2026-08-04 · Spec: ../spec/2026-08-04-toi-uu-token-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — việc là viết 1 script nhỏ + 1 file đề xuất, chia subagent hay giao engine ngoài tốn nhiều hơn tiết kiệm (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (mode main) · ĐÓNG SỔ 2026-08-04 — 19/19 task xong

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| tavily-search | T2.3 | `docs/tdq/research/2026-08-04-toi-uu-token-workflow.md` có mục "Phần 4 — Xác minh" ≥3 dòng nguồn |
| claude-md-improver | T2.4 | `docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md` có mục "Nhóm C" kèm bảng giữ/cắt từng mục CLAUDE.md |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy test của phase đó, phải xanh mới sang phase sau. Full suite chỉ chạy ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Không sửa CLAUDE.md, skill, hook, script workflow — lần này chỉ viết đề xuất.

## P1 — Script đo `token_audit.py`

- [x] **T1.1** Viết `tests/test_token_audit.py`: dựng 1 file jsonl giả trong thư mục tạm, khẳng định `carry_cost()` trả đúng `len(s)//4 × số api_call còn lại` — Test: `cd tests && python3 -m unittest test_token_audit` → FAIL (chưa có module)
- [x] **T1.2** Viết `scripts/token_audit.py`: hàm `iter_events(path)` bỏ qua dòng jsonl hỏng, `carry_cost(events)` trả bảng theo nhóm tool — Test: `cd tests && python3 -m unittest test_token_audit` → OK
- [x] **T1.3** Thêm CLI: `python3 scripts/token_audit.py [--project <dir>] [--sessions N]` in bảng nhóm + tổng, exit 0 khi không có session (chỉ cảnh báo) — Test: `python3 scripts/token_audit.py --sessions 2` → exit 0, output chứa `carry-cost`
- [x] **T1.4** Log service: mỗi bước in `[ISO8601] ...` ra stderr, tắt bằng `TDQ_AUDIT_LOG=0` — Test: `TDQ_AUDIT_LOG=0 python3 scripts/token_audit.py 2>&1 >/dev/null | wc -l` → `0`

**Xong P1 khi**: `cd tests && python3 -m unittest test_token_audit` OK và 2 lệnh CLI trên exit 0.

## P2 — Chốt số liệu & nguồn

- [x] **T2.1** Chạy `token_audit.py` trên project này, lưu output thật vào `docs/tdq/research/<slug>.md` mục "Phần 1b — Số đo lặp lại được" — Test: `grep -c 'Phần 1b' docs/tdq/research/2026-08-04-toi-uu-token-workflow.md` → `1`
- [x] **T2.2** Lập bảng nguyên nhân ≥10 dòng, mỗi dòng có số đo + nguồn số đo — Test: đếm dòng bảng "Nguyên nhân" trong file đề xuất ≥10, không dòng nào thiếu số
- [x] **T2.3** Xác minh lại 3 khẳng định ngoài (progressive disclosure, subagent context riêng, ngưỡng context) bằng nguồn chính thức — Test: `grep -c 'https://' docs/tdq/research/2026-08-04-toi-uu-token-workflow.md` → ≥3
  - Dùng: `tavily-search` (mcp)
  - Nạp: gọi skill `tavily-search` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/.../tavily/skills/tavily-search/SKILL.md` rồi làm theo.
  - Để: chạy truy vấn qua `tavily-primary`, chắt lọc còn ≤3 dòng/nguồn trước khi ghi file.
  - Ra: mục "Phần 4 — Xác minh" trong `docs/tdq/research/2026-08-04-toi-uu-token-workflow.md`.
  - Kiểm: `grep -c 'Phần 4' docs/tdq/research/2026-08-04-toi-uu-token-workflow.md` → `1`
  - Không dùng cho: research chủ đề mới ngoài 3 khẳng định trên.
- [x] **T2.4** Audit `~/.claude/CLAUDE.md`: liệt kê từng mục 1–10, đo ký tự, phán quyết GIỮ/CẮT/CHUYỂN-SANG-SKILL kèm lý do — Test: bảng mục "Nhóm C" có đủ 10 dòng, mỗi dòng có số ký tự
  - Dùng: `claude-md-improver`
  - Nạp: gọi skill `claude-md-improver` TRƯỚC bước đỏ của task này. Agent ngoài không có skill system: đọc `~/.claude/plugins/.../claude-md-management/skills/claude-md-improver/SKILL.md` rồi làm theo.
  - Để: chấm chất lượng từng mục CLAUDE.md và đề xuất bản lõi, KHÔNG ghi đè file thật.
  - Ra: mục "Nhóm C" trong `docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md`.
  - Kiểm: `grep -c '^## Nhóm C' docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md` → `1`
  - Không dùng cho: sửa trực tiếp `~/.claude/CLAUDE.md` (ngoài phạm vi spec §1).

**Xong P2 khi**: bảng nguyên nhân ≥10 dòng có số đo, mục Phần 4 và Nhóm C đã có.

## P3 — Viết file đề xuất

- [x] **T3.1** Dựng khung `docs/tdq/knowledge/2026-08-04-de-xuat-toi-uu-token.md`: mô hình chi phí, bảng nguyên nhân, 5 heading `## Nhóm A`…`## Nhóm E` — Test: `grep -c '^## Nhóm' <file>` → `5`
- [x] **T3.2** Nhóm A — cắt carry-cost của việc đọc: spec/plan đọc lại, Read cả file, Bash ồn. Cần ≥4 task, mỗi task có cột tiết kiệm ước tính + rủi ro — Test: bảng Nhóm A ≥4 dòng, không ô trống
- [x] **T3.3** Nhóm B — đẩy việc nặng sang subagent (research, đọc code, QC): ≥2 task kèm cách trả digest ≤1k ký tự — Test: bảng Nhóm B ≥2 dòng, không ô trống
- [x] **T3.4** Nhóm C — cắt context nền (CLAUDE.md lõi + references nạp lười, chia nhỏ `tdq-build/SKILL.md`): ≥2 task — Test: bảng Nhóm C ≥2 dòng, không ô trống
- [x] **T3.5** Nhóm D — giảm số API call (gộp Bash/Edit, test theo module, CLI im lặng): ≥3 task — Test: bảng Nhóm D ≥3 dòng, không ô trống
- [x] **T3.6** Nhóm E — giảm output token & vệ sinh session (gộp doc, cap dòng spec/plan/log, 1 request 1 session): ≥2 task — Test: bảng Nhóm E ≥2 dòng, không ô trống
- [x] **T3.7** Mục "Thứ tự làm": xếp mọi task theo hạng P0/P1/P2 = tiết kiệm ÷ công sức, kèm tổng tiết kiệm ước tính — Test: `grep -c 'P0\|P1\|P2' <file>` → ≥12
- [x] **T3.8** Mục "Giả định & cách kiểm chứng lại": ghi công thức của từng ước lượng + cách đo lại bằng `token_audit.py` — Test: mục tồn tại, mỗi ước lượng có công thức

**Xong P3 khi**: file đề xuất có đủ 5 nhóm, ≥12 task, bảng ưu tiên và mục giả định.

## P4 — QC & Report

- [x] **T4.1** Chạy Q1–Q10 của spec §6, ghi bằng chứng (lệnh + output thật) vào `docs/tdq/qc/2026-08-04-toi-uu-token-workflow.md` — Test: mọi hạng mục PASS
- [x] **T4.2** Chạy full test suite đúng MỘT lần (kiểm không làm hỏng test cũ) — Test: `cd tests && python3 -m unittest discover -s . -p "test_*.py"` → OK
- [x] **T4.3** Viết `docs/tdq/reports/2026-08-04-toi-uu-token-workflow.md` ≤50 dòng, đóng sổ plan, append working log — Test: `wc -l <report>` ≤ 50

**Xong P4 khi**: QC toàn PASS, report ≤50 dòng, mọi task tick `[x]`.

## Definition of Done

Trỏ về spec §6:

| # | Lệnh kiểm | PASS khi |
|---|---|---|
| Q1 | `grep -c '^## Nhóm' <đề xuất>` | = 5 |
| Q2 | đếm dòng bảng task trong 5 nhóm | ≥12, không ô trống |
| Q3 | đếm dòng bảng nguyên nhân | ≥10, mỗi dòng có số |
| Q4 | `grep -c 'P0\|P1\|P2' <đề xuất>` | ≥12 |
| Q5 | `python3 scripts/token_audit.py` | exit 0, in bảng carry-cost |
| Q6 | `cd tests && python3 -m unittest test_token_audit` | OK |
| Q7 | `TDQ_AUDIT_LOG=0 python3 scripts/token_audit.py 2>&1 >/dev/null \| wc -l` | `0` |
| Q8 | `python3 scripts/doc_lint.py --pair <spec> <plan>` | exit 0 |
| Q9 | `wc -l <report>` | ≤50 |
| Q10 | `git status --porcelain` | chỉ docs/tdq, docs/workinglog, scripts/token_audit.py, tests/test_token_audit.py |
