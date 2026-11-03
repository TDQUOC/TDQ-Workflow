# PLAN — Đổi nhãn lane: `chế độ nhanh (express)` / `chế độ chuyên sâu (deep)`

Ngày: 2026-08-12 · Spec: ../spec/2026-08-12-doi-ten-lane.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — việc trải mỏng trên 34 file văn bản nhưng lõi mã chỉ 3 file; tách
worktree cho sub-agent tốn hơn phần tiết kiệm được (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Lõi: nhãn và bí danh trong `tdq_state.py`
- [x] **T1.1** (n3 e10m) Thêm `LANE_LABELS` + `lane_label(lane)` vào `scripts/tdq_state.py`; lane lạ trả lại nguyên chuỗi — Test: `tests/test_lane_label.py` mới: `lane_label("quick") == "chế độ nhanh (express)"`, `lane_label("full") == "chế độ chuyên sâu (deep)"`, `lane_label("xyz") == "xyz"`
- [x] **T1.2** (n5 e15m) Thêm `LANE_ALIASES` + `normalize_lane(text)`: `nhanh|express|quick → quick`, `chuyen-sau|chuyensau|chuyên sâu|deep|full → full`, không khớp → `None` — Test: cùng file, bảng tham số cho 10 đầu vào kể cả `"QUICK"` hoa và chuỗi rác
- [x] **T1.3** (n5 e12m) `init <slug> <lane>` chạy đầu vào qua `normalize_lane`, thông báo lỗi liệt kê nhãn mới — Test: `TDQ_PROJECT_DIR=<tmp> python3 scripts/tdq_state.py init t express` → `state.json` có `lane == "quick"`
- [x] **T1.4** (n5 e12m) `approve <target>` nhận `nhanh`/`express` như bí danh của `quick` (vẫn ghi khoá `quick_approved*`) — Test: `TDQ_PROJECT_DIR=<tmp> ... approve nhanh` ghi đúng `quick_approved=true`
- [x] **T1.5** (n3 e10m) `USAGE` và mô tả lane trong `PHASE_TABLE` dùng nhãn mới; chạy lại `phases-doc --plugin-root > skills/tdq-conventions/references/phases.md` — Test: `python3 -m pytest tests/test_quick_qc.py -q` xanh (gồm `test_phases_doc_regenerated`)

**Xong P1 khi**: `python3 -m pytest tests/ -q` xanh và `init t express` ghi `lane=quick`.

## P2 — Hook: nhận câu duyệt bằng từ mới
- [x] **T2.1** (n5 e15m) Mở rộng regex `hooks/scripts/prompt_context.py:26` để "duyệt nhanh"/"duyệt express" đi đúng nhánh như "duyệt quick"; `nhanh` đứng một mình KHÔNG khớp — Test: `tests/test_prompt_context.py` thêm ca dương (`duyệt nhanh`) và ca âm (`làm nhanh giúp tôi`)
- [x] **T2.2** (n5 e12m) `APPROVE_CLI` ở `hooks/scripts/bash_gate.py:42` nhận `approve nhanh|express` — Test: `tests/test_bash_gate.py` thêm ca cho lệnh CLI bí danh
- [x] **T2.3** (n3 e8m) `APPROVE_HINTS` ở `hooks/scripts/_common.py:29` gợi ý `duyệt nhanh`, vẫn nêu `quick` chạy được, không vượt `trim()` — Test: ca kiểm độ dài ≤3 dòng/200 ký tự sau `trim()`

**Xong P2 khi**: câu cũ và câu mới cùng khớp, ca âm không khớp, full-suite xanh.

## P3 — Văn bản người đọc
- [x] **T3.1** (n5 e20m) Đổi cách gọi lane trong 6 skill `tdq-*` (`skills/**`, ~62 dòng) sang nhãn mới; giữ nguyên tên file `quick-lane.md` và mọi chuỗi định danh trong ví dụ lệnh — Test: `grep -rn 'lane quick\|lane full' skills/` → 0 dòng
- [x] **T3.2** (n5 e15m) Đồng bộ `portable/**` (~41 dòng) theo T3.1 — Test: `grep -rn 'lane quick\|lane full' portable/` → 0 dòng
- [x] **T3.3** (n3 e10m) `README.md` + `.claude-plugin/plugin.json` mô tả dùng nhãn mới — Test: `grep -c 'chế độ nhanh' README.md .claude-plugin/plugin.json` → cả hai ≥1
- [x] **T3.4** (n3 e10m) Ba script canvas (`canvas_a4_ch4_ch7.py`, `canvas_layout_apply.py`, `claude_export.py`): đổi chuỗi là chữ người đọc, không đụng khoá dữ liệu — Test: `python3 -m pytest tests/ -q` xanh và grep 3 file không còn "lane quick & full"

**Xong P3 khi**: không còn cách gọi cũ trong chữ sống; `git diff --stat docs/tdq/` không có file lịch sử nào bị sửa.

## P4 — Log & test bắt buộc
Log: BỎ — việc này chỉ đổi chuỗi hiển thị và thêm bảng tra bí danh, không sinh runtime mới.
- [x] **T4.1** (n3 e10m) `tests/test_lane_label.py` phủ đủ `lane_label` + `normalize_lane` + hai đường CLI, chạy bằng một lệnh — Test: `python3 -m pytest tests/test_lane_label.py -q` xanh
- [x] **T4.2** (n3 e10m) Viết mục `## 0.11.4 — 2026-08-12` vào `CHANGELOG.md` và bump `.claude-plugin/plugin.json` → `0.11.4` — Test: `head -12 CHANGELOG.md | grep -c '0.11.4'` → `1` và `doc_lint.py CHANGELOG.md` sạch

## Definition of Done
Trỏ về §6 của spec:
1. `python3 -m pytest tests/ -q` xanh, số test ≥ 479.
2. `TDQ_PROJECT_DIR=<tmp> ... init t express` → `lane` trong state là `quick`.
3. Regex khớp `duyệt quick` như trước.
4. Regex khớp `duyệt nhanh` và `duyệt express`; KHÔNG khớp `làm nhanh giúp tôi`.
5. `grep -rn 'lane quick\|lane full' skills/ portable/ README.md` → 0 dòng.
6. `git diff --stat docs/tdq/` — không file lịch sử nào bị sửa.
7. `test_phases_doc_regenerated` PASS.
8. `python3 scripts/doc_lint.py CHANGELOG.md docs/tdq/spec/2026-08-12-doi-ten-lane.md` sạch.

## QC
- Q1 test từng task (T1.1–T4.2): PASS — chạy đúng lệnh `Test:` của từng task; bằng chứng gộp ở Q2–Q9.
- Q2 DoD1 "full-suite xanh, ≥479 test": PASS — `python3 -m pytest tests/ -q` → `493 passed, 178 subtests passed in 35.89s`
- Q3 DoD2 "init express ghi lane=quick": PASS — `TDQ_PROJECT_DIR=<tmp> ... init 2026-08-12-t express` → state có `lane` = `quick`
- Q4 DoD3 "câu duyệt cũ vẫn khớp": PASS — `looks_like_approval("duyệt quick","quick")` → `True`
- Q5 DoD4 "câu mới khớp, câu bẫy không khớp": PASS — `duyệt nhanh`/`duyệt express` → `True`; `làm nhanh giúp tôi`, `ok làm nhanh nhé` → `False`
- Q6 DoD5 "hết cách gọi cũ": PASS — `grep -rn 'lane quick\|lane full' skills/ portable/ README.md` → `0` dòng
- Q7 DoD6 "tài liệu lịch sử nguyên vẹn": PASS — `git diff --stat docs/tdq/` chỉ đụng `STATE.md` (tự sinh) và plan của request TRƯỚC (tick + QC ghi từ turn trước, `git log` xác nhận); không file lịch sử nào bị request này sửa
- Q8 DoD7 "phases.md khớp bộ sinh": PASS — `pytest -k phases_doc` → `1 passed`
- Q9 DoD8 "lint tài liệu": PASS — `doc_lint.py CHANGELOG.md spec plan` → exit `0`

### Vòng fix trong lúc implement (đã đóng)
- F1 `doc_lint` R5: câu 44 từ ở `quick-lane.md:3` → tách hai câu. Xanh.
- F2 `test_quick_qc` khoá cứng heading `## QC ở quick` → đổi kỳ vọng sang `## QC ở chế độ nhanh` (khẳng định về CHỮ trong doc, không phải định danh). Xanh.
- F3 `test_token_budget` tổng description skill 937 > 900 ký tự do nhãn dài hơn → rút gọn 3 description, còn 900. Xanh.

