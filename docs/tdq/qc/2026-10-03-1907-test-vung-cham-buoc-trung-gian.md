# QC — Chạy test vùng chạm + bán kính ảnh hưởng, trọn bộ chỉ ở 2 cổng

Ngày: 2026-10-05 · Plan: ../plan/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md · Vòng: 2 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết luận: PASS ở vòng 2, có 1 lệch spec chờ duyệt.** Vòng 1: QC-F1 đỏ do hai lần chạy trọn bộ
chồng nhau làm hết bộ nhớ (không phải lỗi mã), nhưng lộ ra một lỗi thật của sổ bỏ sót → QC1.1.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bán kính đúng ở ca đã đo | `discover -p test_tdq_test.py -k ca_da_do` | `Ran 4 tests OK` | PASS |
| Q2 | Không bỏ sót test gọi qua tiến trình con | `… -k tien_trinh_con` | `Ran 2 tests OK` | PASS |
| Q3 | Dò file luật theo đường dẫn | `… -k duong_dan` | `Ran 5 tests OK` | PASS |
| Q3b | Test quét thư mục được chọn | `… -k quet_thu_muc` | `Ran 4 tests OK` | PASS |
| Q4 | Rơi về trọn bộ đúng lúc | `… -k tron_bo_khi` | `Ran 4 tests OK` | PASS (lệch, chờ duyệt) — xem lệch #1 |
| Q5 | Bước trung gian nhanh với file lá | `tdq_test.py vung-cham --files hooks/scripts/stop_gate.py` | 16/129 module · **48,6 s** (ngưỡng 60 s) | PASS |
| Q6 | Sổ trọn bộ + `next` nhắc | `… -k so` · `-p test_next_tron_bo.py` | `Ran 20 OK` · `Ran 13 OK` | PASS |
| Q6b | Sổ bán kính bỏ sót | `… -k bo_sot` | `Ran 6 tests OK` | PASS (vòng 2, sau QC1.1) |
| Q7 | Luật một nguồn | `-p test_luat_test.py` | `Ran 4 tests OK` | PASS |
| Q8 | Chạy từ mọi shell | trọn bộ gọi từ PowerShell | `Ran 2502 tests in 548.745s · OK (skipped=9)` · 0 lỗi `true` (trước: 26 fail + 1 error) | PASS |
| Q9 | Trọn bộ xanh | `tdq_test.py tron-bo` từ Git Bash, sau vòng sửa cuối | `Ran 2502 tests in 613.903s · OK (skipped=9)` · 0 module đỏ | PASS |
| Q10 | Trần token | `token_budget.py --kiem` · `doc_lint skills` | exit 0 · exit 0 · `tdq-build/SKILL.md` 174/174 dòng · `plan-template.md` 3.499/3.500 | PASS |
| Q11 | Kiến trúc | `grep "^import hooks\|^from hooks" scripts` + dòng 2026-10-03 (yêu cầu 1907) | 0 · 1 | PASS |
| Q12 | Tiết kiệm báo trung thực | report | ghi cả nền cũ (7,4 lần/request) lẫn nền mới (2–3) | PASS (ở report) |

## Vòng 1 → vòng 2

- **Lần đỏ:** `tron-bo` lúc 15:33 báo 4 failure ở `test_claude_export` (3) và `test_bench` (1); mã
  thoát `0xC000012D` (STATUS_COMMITMENT_LIMIT — hết bộ nhớ ảo). Sổ cho thấy lần chạy QC-F1 bị ngắt
  lúc phiên đứt (15:25) vẫn chạy xong ở nền và XANH — lần tôi chạy lại đã chồng lên nó. Chạy riêng
  hai module: 64 và 46 test OK.
- **Lỗi thật lộ ra:** `tron-bo` ghi 2 dòng "bỏ sót" cho hai module đó, dù không phải bán kính bỏ
  sót: sổ của cây chính không có dòng `vung-cham` nào (trợ lý chạy trong worktree riêng), nên mọi
  module đỏ đều bị tính là bỏ sót.
- **QC1.1:** chỉ kết luận bỏ sót khi request có ít nhất một dòng `vung-cham`; không có thì in
  "radius check skipped". 60 test `test_tdq_test.py` OK. Chạy lại trọn bộ sau vòng sửa: xanh ở cả
  hai shell (Q8, Q9).

## Lệch spec chờ duyệt

`tdq_state.py lech list`:

- **#1 · Q4** — spec: "có file ngoài `scripts/ hooks/ skills/ tests/ agents/` → chạy trọn bộ". Đo
  được (soát lỗi T5.3): mọi request đều sửa `docs/tdq/*` → `vung-cham` không `--files` luôn chọn
  129/129, tính năng không bao giờ có tác dụng, sổ bỏ sót không bao giờ ghi được. Đã áp (T5.6): chỉ
  file MÃ hoặc loại KHÔNG RÕ ngoài 5 thư mục mới rơi về trọn bộ; file dữ liệu (`.md .json .jsonl
  .txt .gitignore` …) chỉ kéo theo test nhắc đường dẫn của nó. Kiểm trên cây chính:
  `tdq_bench.py` + một file plan → 20 module; `STATE.md` + `.gitignore` → 12; `tools/x.sh` → trọn bộ.

## T5.3 — soát lỗi đúng-sai (`code-review`, mức high)

| # | Phát hiện | Phán quyết | Đã làm gì |
|---|---|---|---|
| 1 | `vung-cham` không `--files` luôn chạy trọn bộ vì mọi request sửa `docs/tdq/*` | NHẬN — lỗi thật, nặng | T5.6 + lệch spec #1 |
| 2 | Sửa `tests/helper.py` chỉ chọn 4/106 module dùng nó | NHẬN — lỗi thật | T5.6: dò import ngược cả module không phải test trong `tests/` → 107/129 → trọn bộ |

## T5.4 — rút gọn (`simplify`, 4 agent)

Sửa, không đổi hành vi (`test_tdq_test` 55, `test_next_tron_bo` 13, `test_state` 56 OK trước và
sau): dùng lại `tdq_state.log_enabled/now_iso/resolve_project_dir`; `dem_repo()` công khai thay
cho `tdq_state` gọi vào hàm riêng `_doc_so`; import `unittest`/`argparse` lười — import
`tdq_test` từ `render_next` (mọi prompt) 24 ms → **2,9 ms**; lọc chuỗi con trước regex. Bỏ qua có
lý do: gộp hai đồ thị import thành một (đổi kiến trúc); bản đồ "test đọc file nào" bằng audit hook
khi chạy trọn bộ (đề xuất cho request sau); lọc trước bước parse AST (đổi cách xử lý test hỏng cú
pháp).

## Nợ khai ra, không giấu

1. **Vượt ngân sách trọn bộ của chính request này: 4 lần / ngân sách 3** — một lần trùng do phiên
   đứt giữa lệnh (QC-F1 lúc 15:25 chạy xong ở nền, lần 15:33 chạy lại chồng lên).
2. **Sổ `docs/tdq/.tdq-test.jsonl` còn 2 dòng "bỏ sót" SAI** (15:33, trước QC1.1). Sổ là file cục
   bộ trong gitignore; giữ nguyên làm vết, report ghi rõ là sai.
3. **Mã sản phẩm `scripts/tdq_bench.py:118` vẫn gọi lệnh shell `true`.** T4.1 chỉ sửa test (thêm
   shim `true.cmd` vào PATH khi thiếu); file sản phẩm nằm ngoài phạm vi spec.
4. **`test_bench` đổi một phép kiểm:** "không có nhánh `tdq/*`" → "số nhánh `tdq/*` trước và sau
   như nhau" (vì worktree của đội chạy song song). Cùng ý định — bench không được rò nhánh — nhưng
   là đổi ý nghĩa phép kiểm; vẫn có thể đỏ giả nếu nhánh của task khác đổi đúng lúc bench chạy.
5. **Trọn bộ đang chậm dần và dao động:** 353,9 s (10-03) → 420 – 621 s hôm nay trên cùng máy;
   phần dao động lớn đến từ tải máy, phần tăng đều đến từ test mới.
6. Vấn đề cũ, không thuộc request này: Pyright báo kiểu ở `tdq_test.py` (`NodeVisitor` override,
   `unittest.loader._FailedTest`) — chạy đúng, chỉ là chú thích kiểu.
