# PLAN — Tổ chức graphify: chỉ scan source, đọc có chủ đích

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-graphify-chi-source.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 6 file hook phụ thuộc chặt vào thứ tự import (`_common` bơm `sys.path` trước), sai thứ tự là cả bộ hook chết; task đụng chung một chuỗi import nên không tách worktree được. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Cấu hình phạm vi quét

- [x] **T1.1** (n2 e5m) Viết lại `.graphifyignore` đủ 8 thư mục (`tests/ docs/ portable/ skills/ agents/ ClaudeExport/ claude-export/ graphify-out/`), kèm comment nêu rõ code mới phải nằm trong `scripts/` hoặc `hooks/` — Test: `grep -c '/$' .graphifyignore` in ra `8`
  - Dùng: `graphify`
  - Để: xác nhận cú pháp `.graphifyignore` và kiểm phạm vi quét sau khi sửa, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Ra: `.graphifyignore` 8 dòng thư mục + comment
  - Kiểm: `graphify extract . --code-only --force` chỉ báo `found` file trong `scripts/` + `hooks/`
  - Không dùng cho: sửa nội dung mã nguồn ở P2 — P2 là việc của Python, không phải của graphify

**Xong P1 khi**: `grep -c '/$' .graphifyignore` = 8 và extract không nạp file ngoài `scripts/`, `hooks/`.

## P2 — Đổi lối import ở tầng hook

- [x] **T2.1** (n6 e14m) `hooks/scripts/_common.py`: giữ `import tdq_state` làm bootstrap `sys.path` + re-export, thêm `from tdq_state import (...)`, đổi 6 chỗ gọi `tdq_state.f()` → `f()` — Test: `grep -c 'tdq_state\.' hooks/scripts/_common.py` = 0 và `python3 -m pytest tests/test_stop_gate.py -q` xanh
- [x] **T2.2** (n7 e18m) `hooks/scripts/prompt_context.py`: đổi 18 chỗ gọi sang from-import, dòng `from tdq_state import ...` đặt SAU `from _common import ...` — Test: `grep -n 'tdq_state\.' hooks/scripts/prompt_context.py | grep -v 'tdq_state\.py' | wc -l` = 0 và `python3 -m pytest tests/test_prompt_context.py tests/test_context_hooks.py -q` xanh
- [x] **T2.3** (n7 e16m) `hooks/scripts/stop_gate.py`: bỏ `tdq_state` khỏi dòng `from _common import`, đổi 15 chỗ gọi — Test: `grep -c 'tdq_state\.' hooks/scripts/stop_gate.py` = 0 và `python3 -m pytest tests/test_stop_gate.py -q` xanh
- [x] **T2.4** (n6 e13m) `hooks/scripts/edit_gate.py`: đổi 12 chỗ gọi — Test: `grep -c 'tdq_state\.' hooks/scripts/edit_gate.py` = 0 và `python3 -m pytest tests/test_edit_gate.py tests/test_gate_merge.py -q` xanh
- [x] **T2.5** (n4 e7m) `hooks/scripts/session_start.py`: bỏ `tdq_state` khỏi dòng `from _common import`, đổi 4 chỗ gọi — Test: `grep -c 'tdq_state\.' hooks/scripts/session_start.py` = 0 và `python3 -m pytest tests/test_context_hooks.py -q` xanh
- [x] **T2.6** (n5 e9m) `hooks/scripts/bash_gate.py`: đổi 3 chỗ gọi — Test: `grep -c 'tdq_state\.' hooks/scripts/bash_gate.py` = 0
- [x] **T2.7** (n5 e10m) `tests/test_bash_gate.py:185`: đổi `mock.patch.object(tdq_state, "turn_log_read", ...)` sang patch chính module `bash_gate` đã nạp, giữ nguyên ý nghĩa phép kiểm (đếm số lần đọc sổ turn) — Test: `python3 -m pytest tests/test_bash_gate.py -q` xanh
  - Dùng: `superpowers:test-driven-development`
  - Để: chạy đúng nhịp đỏ→xanh cho task sửa test này, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `~/.claude/plugins/superpowers/skills/test-driven-development/SKILL.md` rồi làm theo.
  - Ra: `tests/test_bash_gate.py` với patch trỏ vào module hook
  - Kiểm: `python3 -m pytest tests/test_bash_gate.py -q` xanh, và cố ý phá `turn_log_read` thì test đỏ lại
  - Không dùng cho: viết thêm test mới ngoài phạm vi spec §2

**Xong P2 khi**: `grep -n 'tdq_state\.' hooks/scripts/*.py | grep -v 'tdq_state\.py' | wc -l` = 0, `python3 -m pytest tests/ -q` xanh, `echo '{}' | python3 hooks/scripts/prompt_context.py` exit 0.

## P3 — Luật ĐỌC trong workflow

- [x] **T3.1** (n3 e8m) Thêm mục luật ĐỌC vào `skills/tdq-intake/references/analyze-full.md` bước 2 "Đọc code": mở graph khi câu hỏi là "ai gọi X / sửa X ảnh hưởng đâu / cấu trúc tổng thể"; tìm chuỗi và đọc file cụ thể thì grep — Test: `grep -c graphify skills/tdq-intake/references/analyze-full.md` ≥ 1 và `python3 scripts/doc_lint.py` file đó exit 0
- [x] **T3.2** (n3 e6m) Thêm cùng luật (bản rút gọn 1–2 dòng) vào `skills/tdq-intake/references/quick-lane.md` bước 1 — Test: `grep -c graphify skills/tdq-intake/references/quick-lane.md` ≥ 1 và `doc_lint.py` exit 0

**Xong P3 khi**: cả 2 file có luật ĐỌC và qua `doc_lint.py`.

## P4 — Loại `graphify-out` khỏi pathspec turn_snapshot

- [x] **T4.1** (n4 e9m) Thêm test đỏ vào `tests/test_turn_snapshot.py`: đổi file trong `graphify-out/` KHÔNG làm đổi `repo_sha` của `turn_snapshot` — Test: `python3 -m pytest tests/test_turn_snapshot.py -q` ĐỎ đúng test mới
- [x] **T4.2** (n3 e5m) Thêm `"graphify-out"` vào `BOOKKEEPING_PATHS` (`scripts/tdq_state.py`) — Test: `python3 -m pytest tests/test_turn_snapshot.py -q` xanh và `git diff HEAD --name-only -- ':(top)' ':(top,exclude)docs/tdq' ':(top,exclude)docs/workinglog' ':(top,exclude)graphify-out' | grep -c graphify-out` = 0 (không đường dẫn `graphify-out` nào lọt vào diff sau khi loại trừ)

**Xong P4 khi**: test mới xanh, suite đầy đủ xanh.

## P5 — Kiểm đồ thị & chốt

- [x] **T5.1** (n4 e8m) Build lại đồ thị và đo cạnh `hooks/* → scripts/tdq_state.py` — Test: `graphify affected "turn_snapshot()"` ra ≥ 1 node có `prompt_context`, và đếm trong `graph.json` ≥ 20 cạnh cross-file `hooks/* → scripts/tdq_state.py`
  - Dùng: `graphify`
  - Để: extract lại và tra `affected`/`query` để chứng minh đồ thị đã thấy chuỗi hook → state, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Ra: `graphify-out/graph.json` mới + số cạnh ghi vào report
  - Kiểm: `graphify affected "turn_snapshot()"` không in `No affected nodes found.`
  - Không dùng cho: quyết định nội dung luật ĐỌC ở P3 — luật đó user đã chốt ở interview
- [x] **T5.2** (n3 e10m) Viết `docs/tdq/reports/2026-08-14-graphify-chi-source.md` (10–20 dòng): trước/sau, 9 hạng mục QC, việc còn treo — Test: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-14-graphify-chi-source.md` exit 0
- [x] **T5.3** (n2 e3m) Ghi 1 fact vào bộ nhớ dài hạn: graphify 0.9.28–0.9.42 chỉ resolve `from M import f`, không resolve `import M` + `M.f()` — Test: `search_memories` với từ khoá `graphify import` trả về fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu đúng một fact ngắn về giới hạn resolve của graphify cho các session sau, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: 1 memory trong project `TDQWorkflow`
  - Kiểm: `search_memories(query="graphify import", project="TDQWorkflow")` trả về fact đó
  - Không dùng cho: lưu số đo hiệu năng hay nội dung report — report đã có file riêng

## P6 — Log & test bắt buộc

- [x] **T6.1** (n2 e4m) Log service giữ nguyên: `tdq_state` đã có `_warn`/`TDQ_LOG` bật mặc định kèm timestamp, tắt được qua env — task này chỉ xác nhận đổi import không làm mất đường log — Test: `TDQ_LOG=1 echo '{}' | python3 hooks/scripts/prompt_context.py 2>&1 | grep -c '\['` ≥ 1
- [x] **T6.2** (n2 e5m) Suite đầy đủ chạy bằng một lệnh — Test: `python3 -m pytest tests/ -q` in `535 passed` trở lên, 0 failed

## Definition of Done

Trỏ về §6 của spec. Mỗi dòng một lệnh kiểm:

1. Q1 — `grep -c '/$' .graphifyignore` in ra `8`
2. Q2 — `grep -n 'tdq_state\.' hooks/scripts/*.py | grep -v 'tdq_state\.py' | wc -l` in ra `0` (loại trừ chuỗi lệnh `tdq_state.py` in cho user, không phải lời gọi)
3. Q3 — `python3 -m pytest tests/ -q` in `535 passed` trở lên, 0 failed
4. Q4 — `echo '{}' | python3 hooks/scripts/prompt_context.py; echo $?` in `0`
5. Q5 — `graphify affected "turn_snapshot()"` ra ≥ 1 node, có `prompt_context`
6. Q6 — đếm cạnh cross-file `hooks/* → scripts/tdq_state.py` trong `graph.json` ≥ 20
7. Q7 — `git diff HEAD --name-only -- ':(top)' ':(top,exclude)docs/tdq' ':(top,exclude)docs/workinglog' ':(top,exclude)graphify-out' | grep -c graphify-out` in `0`, và `pytest tests/test_turn_snapshot.py -q` xanh (test `test_digest_ignores_graphify_out`)
8. Q8 — `grep -c graphify skills/tdq-intake/references/analyze-full.md skills/tdq-intake/references/quick-lane.md` mỗi file ≥ 1
9. Q9 — `python3 scripts/doc_lint.py <các file .md đổi>` exit 0
