# QC — Áp Gói đầy đủ (Đ1–Đ7)

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-ap-goi-day-du.md · Spec: ../spec/2026-08-14-ap-goi-day-du.md

Lệnh đếm mệnh lệnh dùng chung cho cả bảng:
`cat <cụm file> | grep -cEi "cấm|bắt buộc|phải |không được|luôn |dừng|ngay"`.
Đếm theo **cụm file** vì luật đi cùng đoạn văn — đề xuất nào dời nội dung giữa hai file mà
đếm rời sẽ báo sai.

## Mốc trước (T0.1, đo lúc 13:33 ngày 2026-08-14)

| Đề xuất | File / cụm file | luật trước | luật sau | phán quyết |
|---|---|---|---|---|
| Đ1 | `skills/tdq-intake/references/analyze-full.md` | 5 | 6 | TĂNG ✓ |
| Đ1 | `skills/tdq-intake/references/skill-inventory.md` | 4 | 6 | TĂNG ✓ |
| Đ2 | `skills/tdq-intake/SKILL.md` + `references/quick-lane.md` | 21 | 25 | TĂNG ✓ |
| Đ3 | `skills/tdq-build/SKILL.md` + `references/qc.md` + `references/report-template.md` | 23 | 32 | TĂNG ✓ |
| Đ4 | `skills/tdq-conventions/references/reminder-codes.md` | 5 | 5 | GIỮ ✓ |
| Đ4 | `skills/tdq-conventions/references/plugin-routing.md` | 2 | 2 | GIỮ ✓ |
| Đ4 | `skills/tdq-conventions/references/tavily.md` | 0 | 0 | GIỮ ✓ |
| Đ5 | `skills/tdq-intake/references/scope-round.md` | 8 | 8 | GIỮ ✓ |
| Đ6 | 8 file nhắc lại (build/SKILL, report-template, spec/SKILL, plan/SKILL, status/SKILL, quick-lane, skill-inventory, mode-gate) | 72 | 85 | TĂNG ✓ |
| Đ7 | `agents/tdq-implementer.md` + `tdq-qc-tester.md` + `tdq-reviewer.md` | 3 | 4 | TĂNG ✓ |

**Phán quyết cuối: 0/10 dòng giảm.** 7 dòng tăng, 3 dòng giữ nguyên, 0 dòng giảm.
(Chốt P1 là 5 tăng / 5 giữ; hai dòng Đ1 lên 6 và cụm Đ6 lên 85 sau khi T3.6 thêm luật cờ `--loc`.)
Đ2 vượt cả mốc luật KHÁC NHAU (17): số thô 25 > 21 nghĩa là trùng lặp mất đi, luật thì không.

Ghi chú cách đếm Đ2: 21 là số đếm THÔ của cặp file. Bốn mệnh lệnh trong Phần C của
`tdq-intake/SKILL.md` đều đã có bản đầy đủ trong `quick-lane.md`, nên đếm theo luật KHÁC
NHAU là 17. Sau Đ2, số thô phải ≥ 17 (trùng lặp biến mất, luật thì không).

### Số đo khác của mốc trước

| Chỉ số | Lệnh | Trước | Sau |
|---|---|---|---|
| `wc -w` reminder-codes.md | `wc -w` | 642 | 645 (+3 = nhãn `## Phụ lục`, 0 từ mất) |
| `wc -w` plugin-routing.md | `wc -w` | 401 | 404 (+3, 0 từ mất) |
| `wc -w` tavily.md | `wc -w` | 314 | 317 (+3, 0 từ mất) |
| dòng `tdq-intake/SKILL.md` | `wc -l` | 109 | 86 (−23) |
| dòng `tdq-build/SKILL.md` | `wc -l` | 116 | 84 (−32) |
| bước đánh số ở `quick-lane.md` | `grep -c "^[0-9]\. "` | 3 | 12 |
| từ mơ hồ ở `scope-round.md` | `grep -cEi "phù hợp\|nếu cần\|tối ưu\|hợp lý\|linh hoạt"` | 2 | 0 |
| file có "nhắc lại có chủ ý" | `grep -rl … skills/ \| wc -l` | 0 | 8 |
| khối ``` trong 3 file agent | `grep -c '^```'` | 0 / 0 / 0 | 2 / 2 / 2 |
| thân `tdq-build/SKILL.md` | `context_surface.py --quiet` | 1.936 token | 1.536 (−21%) |
| thân `tdq-intake/SKILL.md` | `context_surface.py --quiet` | 1.844 token | 1.288 (−30%) |
| TỔNG tầng `nạp khi gọi skill` | `context_surface.py --quiet` | 8.473 token | **7.579 (−894, −10,6%)** |
| TỔNG tầng `đọc khi cần` | `context_surface.py --quiet` | 43.981 token | 46.188 (+2.207 — chỗ nội dung dời xuống) |
| output `skill_inventory.py` mặc định | `wc -c` | 39.722 byte | 39.722 (không đổi, diff rỗng) |
| output `skill_inventory.py --loc "workflow"` | `wc -c` | (không có cờ) | **1.845 byte (−95,4%)** |
| `pytest tests/ -q` | | 563 passed | **569 passed, 241 subtests, 0 failed** |

Baseline output đầy đủ của `skill_inventory.py` lưu ngoài repo tại scratchpad phiên
(`baseline_inv.txt`, 39.722 byte) — dùng cho phép `diff` ở Q8.

## Ảnh hưởng Đ1

Tra bằng `graphify` trước khi đụng `scripts/skill_inventory.py` (T3.1).

- `graphify affected scripts/skill_inventory.py` → exit 0, "No affected nodes found"
  (đồ thị đánh khoá node theo id `scripts_skill_inventory`, không theo đường dẫn file).
- `graphify affected scripts_skill_inventory_inventory` → exit 0, 1 nơi gọi:
  `main() [calls] scripts/skill_inventory.py:L209`. Vậy `inventory()` chỉ có ĐÚNG MỘT
  caller trong mã — chính `main()` của cùng file; sửa chữ ký `main(argv)` không lan ra module khác.
- Cạnh trong `graphify-out/graph.json` chạm `skill_inventory`: 26, toàn bộ là `contains` /
  `calls` nội bộ + 1 `imports` sang `scripts/tdq_state` (dùng `_warn`/`_info`). Không module
  nào import ngược lại `skill_inventory`.
- Caller NGOÀI mã (grep, graphify không bắt vì là văn bản):
  `tests/test_skill_inventory.py` (chạy script bằng subprocess) ·
  `skills/tdq-intake/references/analyze-full.md:7` và
  `skills/tdq-intake/references/skill-inventory.md:13` (dòng lệnh B0 hướng dẫn) ·
  `scripts/tdq_state.py:565` (dòng checklist phase `analyze` nhắc chạy lệnh).
  → Đây đúng là 2 file `.md` mà T3.6 phải cập nhật; `tdq_state.py:565` chỉ là chuỗi mô tả
  lệnh không cờ, vẫn đúng sau khi thêm cờ nên KHÔNG sửa (giữ phạm vi plan).

mem0 (T3.2, project `TDQWorkflow`):
- mem0: fact `2026-08-14-toi-uu-llm-workflow` xác nhận chỗ phí lớn nhất là `skill_inventory.py`
  in 39.722 byte ≈ 9.774 token mỗi lần analyze, và Đ1 được tách khỏi "Gói vừa" thành việc riêng.
- mem0: fact cắt token 2026-08-09 nêu bảng kiểm kê 242 skill nay chỉ ghi dòng DÙNG/NỀN + 1 dòng
  tổng — nghĩa là bản thân brief đã lọc sẵn, nên cắt ở tầng công cụ (cờ `--loc`) là bước còn thiếu.
- mem0: không có fact nào cấm đổi giao diện dòng lệnh của `skill_inventory.py`.

## Chạy thử model hạng thấp (Q15, T5.2)

Sub-agent model **haiku** (hạng thấp), read-only, nhận một yêu cầu giả định
("Thêm cờ `--json` cho `scripts/context_surface.py`") và chỉ được dựa vào các file skill
ĐÃ SỬA để kể lại nó sẽ làm gì. 9 tool call, 76 giây.

Kết quả: **không bỏ bước nào.** Nó ra đúng đường: tầng `nhỏ` vỡ ở điều kiện 1 → mở request →
brief → hỏi lane → DỪNG → `init` → chín bước của `quick-lane.md` (đủ 9, đúng thứ tự, có tick
`[~]`/`[x]`, QC mặc định BẬT, trần 3 vòng fix) → hỏi commit → `phase=idle`.

Điểm cần chú ý nhất của Đ3 — hai mục chỉ còn DÒNG TRỎ (Phần B, Phần C của `tdq-build`) —
đã được kiểm đúng thứ định kiểm: agent MỞ file được trỏ tới thật, dẫn nguồn tới
`quick-lane.md:chín bước 7/8/9` và `report-template.md:Bốn bước 10`, và tự nêu rằng đây là
chỗ "dễ bỏ". Nói cách khác dòng trỏ + câu "BẮT BUỘC mở file đó" đủ để model hạng thấp
không làm theo trí nhớ.

Ghi nhận thêm (không phải lỗi): agent nhắc đúng rằng lane quick ghi QC inline vào plan chứ
không tạo file `qc/` riêng — tức nó phân biệt được nhánh quick và nhánh full sau khi Đ2 dời
luật quick sang `quick-lane.md`.

Q15 là hạng mục quan sát, không dùng làm cổng chặn (spec §6).

## Bảng QC (điền ở T5.1)

| # | Hạng mục | Lệnh | Kết quả | Phán quyết |
|---|---|---|---|---|
| Q1 | Đ2 chuyển đúng chỗ | `grep -c "" skills/tdq-intake/SKILL.md` · `grep -c "^[0-9]\. " …/quick-lane.md` | 86 dòng (109 → 86, giảm 23 ≥ 20) · 12 bước (≥ 9) | PASS |
| Q2 | Đ3 chuyển đúng chỗ | `context_surface.py --quiet \| grep tdq-build/SKILL.md` | thân 1.936 → **1.536 token** (−21%) | PASS theo đích mềm 1A (token giảm); ngưỡng tham chiếu 1.400 KHÔNG đạt — phần còn lại của thân nằm ngoài phạm vi T1.2 |
| Q3 | Đ4 giữ 100% câu chữ | `diff <(git show HEAD:f \| tr -s '[:space:]' '\n' \| sort) <(tr … < f \| sort) \| grep -c '^<'` · `grep -c '^## Phụ lục'` | 0 từ mất ở cả 3 file; `wc -w` 642→645, 401→404, 314→317 (+3 = đúng nhãn `## Phụ lục`) · = 1 | PASS (đọc "bằng nhau" = 0 từ mất; thêm nhãn thì tổng buộc phải +3) |
| Q4 | Đ5 hết từ mơ hồ | `grep -cEi "phù hợp\|nếu cần\|tối ưu\|hợp lý\|linh hoạt" …/scope-round.md` | 0 (trước: 2) | PASS |
| Q5 | Đ6 khai đủ 8 chỗ | `grep -rl "nhắc lại có chủ ý" skills/ \| wc -l` | 8 | PASS |
| Q6 | Đ7 có khối định dạng | `grep -c '^\`\`\`' agents/*.md` | implementer 2 · qc-tester 2 · reviewer 2 | PASS |
| Q7 | Đ1 lọc thật sự nhỏ hơn | `skill_inventory.py --loc "workflow" \| wc -c` vs không cờ | 1.845 vs 39.722 byte (−95,4% ≈ −9.300 token mỗi lần B0) | PASS |
| Q8 | Đ1 giữ nguyên hành vi mặc định | `diff <(skill_inventory.py) baseline_inv.txt` · `diff <(… --tat-ca) baseline_inv.txt` | cả hai RỖNG | PASS |
| Q9 | Đ1 có đường xem đủ | chạy `--loc` rồi đọc dòng cuối | `— Đã ẩn 273 skill không khớp "workflow"; xem đủ: python3 scripts/skill_inventory.py --tat-ca` | PASS |
| Q10 | 2 test mới xanh, không hồi quy | `python3 -m pytest tests/ -q` | **569 passed, 241 subtests passed, 0 failed** (≥ 565) | PASS |
| Q11 | Bảng đối chiếu luật | đếm mệnh lệnh theo 10 cụm file (bảng trên) | 10/10 dòng có "sau" ≥ "trước"; 7 tăng, 3 giữ, **0 giảm** | PASS |
| Q12 | Token tầng nạp giảm | `context_surface.py --quiet` | `nạp khi gọi skill` 8.473 → **7.579** (−894, −10,6%); `đọc khi cần` 43.981 → 46.188 (nội dung dời xuống tầng rẻ) | PASS |
| Q13 | Không lọt phạm vi | `git status --porcelain -- hooks portable` | rỗng | PASS |
| Q14 | Bộ tài liệu hợp lệ | `doc_lint.py --pair <spec> <plan>` | exit 0 | PASS |
| Q15 | Chạy thử model hạng thấp | sub-agent model rẻ chạy thử theo bộ skill mới | xem mục `## Chạy thử model hạng thấp` | (không phải cổng chặn) |

Hai chỗ chệch tiêu chí chữ, ghi minh bạch chứ không nới âm thầm:
- **Q2** — ngưỡng `< 1.400 token` viết ở spec không đạt (dừng ở 1.536). Quyết định 1A của user
  đã đặt số làm THAM CHIẾU, điều kiện thật là "token giảm + số luật không giảm": cả hai đều đạt.
  Muốn xuống dưới 1.400 phải cắt tiếp Phần A của `tdq-build/SKILL.md` — ngoài phạm vi Đ3.
- **Q3** — "số từ bằng nhau" không thể đúng theo nghĩa đen khi Đ4 buộc thêm nhãn `## Phụ lục`.
  Đọc theo nghĩa của Quyết định 4A ("giữ 100% câu chữ") = 0 từ bị mất, đã chứng minh bằng diff từ.

## QC độc lập (T5.3)

Agent `tdq-qc-tester` kiểm lại toàn bộ plan theo DoD, **chỉ đọc, không được sửa file**, tự
chạy lại từng lệnh chứ không tin bảng ở trên. Phán quyết: **PASS Q1–Q14** — trùng khớp T5.1.

| Kiểm | KQ | Bằng chứng agent tự chạy |
|---|---|---|
| Kiểm Q1 | PASS | thân intake 109 → 86 dòng (−23); quick-lane 3 → 12 bước |
| Kiểm Q2 | PASS* | thân build 1.936 → 1.536 token; mốc CỨNG 1.400 không đạt, đích MỀM đạt (luật cụm 23 → 32) |
| Kiểm Q3 | PASS | diff theo từ vs HEAD: `lost=0` cả 3 file; chỉ thêm đúng chữ `Phụ lục` |
| Kiểm Q4 | PASS | từ mơ hồ ở `scope-round.md` 2 → 0 |
| Kiểm Q5 | PASS | `grep -rl "nhắc lại có chủ ý" skills/ \| wc -l` = 8 |
| Kiểm Q6 | PASS | 3 file agent, mỗi file 2 dấu hiệu return-format (2/2/2) |
| Kiểm Q7 | PASS | `--loc "workflow"` 1.845 byte vs mặc định 39.722 byte |
| Kiểm Q8 | PASS | dựng lại baseline từ HEAD = 39.722 byte; diff bản mặc định VÀ `--tat-ca` đều RỖNG |
| Kiểm Q9 | PASS | dòng cuối: `— Đã ẩn 273 skill…; xem đủ: … --tat-ca` |
| Kiểm Q10 | PASS | `569 passed, 241 subtests passed` |
| Kiểm Q11 | PASS | 10 cụm, cột "trước" khớp mốc 13:33; 7 tăng · 3 giữ · **0 giảm** |
| Kiểm Q12 | PASS | tầng `nạp khi gọi skill` 8.473 → 7.579 token (−10,6%) |
| Kiểm Q13 | PASS | `git status --porcelain -- hooks portable` rỗng |
| Kiểm Q14 | PASS | `doc_lint` exit 0 (chạy thêm cho file qc/, skills/, agents/ — đều 0) |

Bốn khiếm khuyết agent nêu và cách xử lý:

1. **Trung bình — "file report không tồn tại".** Agent chạy song song và `ls` TRƯỚC khi
   T5.4 ghi file. Nay `docs/tdq/reports/2026-08-14-ap-goi-day-du.md` đã có, 19 dòng, đủ số
   token trước/sau và số luật trước/sau. Đã hết.
2. **Thấp — số lệch trong sổ.** Plan T1.2 ghi thân build 1.512 token và 116 → 83 dòng; đo
   lại bằng `context_surface.py` là **1.536** và **84** dòng. Đã sửa hai chỗ đó trong plan.
   Riêng cụm Đ6 thì bảng đối chiếu ở trên đã ghi đúng 85 (agent đọc phải bản cũ). Không
   dòng nào đổi phán quyết: mọi số vẫn nằm cùng phía kết luận.
3. **Thấp — nhánh "cấm ẩn nguồn `project`" chỉ có unit test phủ.** Đúng: máy thật hiện có
   0 skill nguồn `project`, nên `--loc zzz` giữ 6 dòng `plugin:tdq-workflow` và 0 dòng
   `project`. GHI NHẬN LÀ GIỚI HẠN, không sửa: viết thêm skill giả vào máy thật chỉ để
   chứng minh là làm bẩn môi trường; `FilterFlagTest` đã dựng đúng tình huống đó trong
   fixture. Đã nêu ở mục Giới hạn của report.
4. **Thông tin — cổng duyệt P2 không có dấu vết trong `state.json`.** Đúng theo thiết kế:
   `tdq_state.py` chỉ có cổng `spec` và `plan`, không có cổng giữa hai phase của cùng một
   plan. Bằng chứng duyệt P2 là câu user nguyên văn `"duyệt phasee max"`, đã chép vào
   header plan. Không tự chế thêm trường state.

