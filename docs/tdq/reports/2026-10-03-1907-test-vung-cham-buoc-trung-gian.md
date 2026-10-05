# REPORT — Chạy test vùng chạm + bán kính ảnh hưởng, trọn bộ chỉ ở 2 cổng (`2026-10-03-1907-test-vung-cham-buoc-trung-gian` · lane full · mode subagent · 14/14 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** script `scripts/tdq_test.py` — `vung-cham` chạy test của vùng chạm + bán kính ảnh hưởng
(test nhắc đường dẫn/tên file, import bắc cầu đọc bằng AST, test quét thư mục cha), rơi về trọn
bộ khi bán kính ≥ 60% hoặc có file mã/không rõ ngoài 5 thư mục; `tron-bo` chạy trọn bộ một tiến
trình và ghi sổ; sổ bán kính bỏ sót; `so` đếm theo ngân sách · `next` nhắc khi trọn bộ vượt số
cổng (chỉ nhắc) · luật một nguồn ở `tdq-build`, khuôn plan, `qc.md`: trọn bộ chỉ ở QC-F1 và sau
vòng sửa QC cuối · 5 module test không còn gọi lệnh `true` → chạy được từ PowerShell.

**Kết quả:**
- Bước trung gian: sửa `stop_gate.py` → 16/129 module, **48,6 s** (trọn bộ 420 – 621 s hôm nay);
  sửa file luật/lá → 7 – 20 module; sửa hub `tdq_state.py` hay `tests/helper.py` → trọn bộ (đúng:
  bán kính thật 98 và 107/129).
- **Tiết kiệm — hai nền, nói thẳng:** so với nền cũ (59 lần trọn bộ / 8 request, TB 7,4), giữ 2 – 3
  lần/request bớt ≈ 4,4 – 5,4 lần × ~400 s ≈ **1.800 – 2.200 s máy/request**. So với nền MỚI (hai
  request gần nhất đã 2 – 3 lần) lợi chỉ khoảng **0 – 400 s**. Giá trị chính là khoá luật cho khỏi
  trôi ngược về 8 – 16 lần, và kiểm thêm vùng ảnh hưởng ở bước trung gian (rộng hơn luật cũ "chỉ
  module đang sửa").
- Chính request này chạy trọn bộ **4 lần / ngân sách 3** — một lần trùng do phiên đứt giữa lệnh.

**Kiểm:** QC `full` **PASS ở vòng 2** — trọn bộ `Ran 2502 tests · OK (skipped=9)` từ Git Bash
(614 s) và PowerShell (549 s, 0 lỗi `true`; trước 26 fail + 1 error) · `code-review` 2 lỗi thật,
sửa ở T5.6 · `simplify`: import `tdq_test` mỗi prompt 24 → 2,9 ms · vòng 1 đỏ vì hai lần trọn bộ
chạy chồng nhau làm hết bộ nhớ (`0xC000012D`), lộ lỗi sổ bỏ sót → QC1.1. QC:
`docs/tdq/qc/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md`.

**Đầu ra:** `scripts/tdq_test.py` (mới) · `scripts/tdq_state.py` (`render_next` nhắc) ·
`skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/plan-template.md`,
`skills/tdq-build/references/qc.md` · `docs/kien-truc.md` · 3 file test mới + 5 file test sửa ·
`.gitignore` (sổ `docs/tdq/.tdq-test.jsonl`) · CHANGELOG 0.57.0 (dời 0.39.0 sang
`docs/CHANGELOG-archive-2.md`). Không sửa gì ngoài repo.

**Lệch spec:** #1 · Q4 — **user đã duyệt ("1a", 2026-10-05)** · ngưỡng "file ngoài 5 thư mục → trọn bộ" → đo được: mọi request
sửa `docs/tdq/*` nên `vung-cham` LUÔN chạy trọn bộ (129/129) · đã áp: chỉ file mã hoặc loại không
rõ ngoài 5 thư mục mới rơi về trọn bộ; file dữ liệu (`.md`, `.json`…) chỉ kéo theo test nhắc
đường dẫn của nó.

**Giới hạn:**
- Sổ cục bộ còn 2 dòng "bỏ sót" SAI (ghi trước QC1.1) — không phải bán kính bỏ sót.
- `scripts/tdq_bench.py:118` (mã sản phẩm) vẫn gọi lệnh `true`; test chỉ được vá bằng shim.
- `test_bench` đổi phép kiểm nhánh `tdq/*` từ "không có" sang "không đổi" — cùng ý định, khác nghĩa.
- Trọn bộ chậm và dao động: 353,9 s (10-03) → 420 – 621 s hôm nay (tải máy + test mới).
- Đề xuất cho request sau: bản đồ "test đọc file nào" bằng audit hook khi chạy trọn bộ — thay phần
  lớn heuristic bán kính bằng số đo.
- macOS/Linux chưa chạy.

**Git:** nhánh `feature/test-vung-cham-buoc-trung-gian`, 48 commit trên `main`, chưa merge. Gồm
commit làm việc của 9 trợ lý và **22 commit sổ sách để mở khoá merge** (`tdq_team.py` từ chối
kiểm/gộp khi bản đồ giao việc cũ hơn plan): `aae2f47` `6c9653d` `97c4dc9` `e1d605b` `6067b76`
`85dd869` `4c807e5` `a4ce8ad` `e7d0885` `1fbac8f` `6e0c611` `65a3188` `7b7352d` `2ae5a57`
`d3ce67e` `ab942f4` `a5d49f4` `019f644` `3aca5f3` `770573c` `85c0c10` `244dd71`. Bản plugin bump
**0.56.0 → 0.57.0**.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 16 min | — | 1 |
| spec | 38 min | — | 1 |
| plan | 42h 14min | — | 1 |
| implement | 59 min | — | 1 |
| qc | 45 min | — | 1 |
| report | 0s | — | 1 |
| **Total** | **44h 53min** | **—** | |

Nguyên văn từ `tdq_timing.py show`. `plan` 42h là thời gian chờ duyệt plan và chọn mode qua cuối
tuần (03-10 → 05-10), không phải thời gian làm. Cột `Model time` là `—` vì công cụ không đọc được
transcript của phiên Windows này (nợ đã khai từ trước).
