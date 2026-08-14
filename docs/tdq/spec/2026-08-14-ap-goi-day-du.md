# SPEC — Áp Gói đầy đủ (Đ1–Đ7) của bản chấm tối ưu LLM

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-ap-goi-day-du.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: thực thi trọn bảy đề xuất Đ1–Đ7 đã viết ở
  `docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`, chia hai phase trong một plan —
  phase văn bản (Đ2–Đ7) xanh trước, phase mã (Đ1) sau — sao cho tổng token nạp giảm mà
  **không dòng nào trong bảng đối chiếu luật có cột "sau" nhỏ hơn cột "trước"**.
- Trong phạm vi:
  - Phase 1 — 17 file văn bản: `skills/tdq-intake/` (SKILL.md, quick-lane.md,
    scope-round.md, skill-inventory.md) · `skills/tdq-build/` (SKILL.md, qc.md,
    report-template.md) · `skills/tdq-conventions/references/` (reminder-codes.md,
    plugin-routing.md, tavily.md) · `skills/tdq-spec/SKILL.md` · `skills/tdq-plan/SKILL.md`
    · `skills/tdq-plan/references/mode-gate.md` · `skills/tdq-status/SKILL.md` ·
    `agents/tdq-implementer.md` · `agents/tdq-qc-tester.md` · `agents/tdq-reviewer.md`.
  - Phase 2 — 4 file: `scripts/skill_inventory.py` (thêm cờ lọc) ·
    `tests/test_skill_inventory.py` (thêm 2 test) · `references/analyze-full.md:7` và
    `references/skill-inventory.md:10` (đổi dòng lệnh gọi).
  - Một cổng duyệt THÊM giữa hai phase (user chọn 2B).
  - Một lần chạy thử bằng model hạng thấp qua sub-agent (user chọn 3B).
- NGOÀI phạm vi:
  - `hooks/` — bản chấm đã chứng minh hook không phải chỗ phí (trung vị ≤ 56,2 ms,
    ≤ 2.075 byte/lượt).
  - `portable/` — 12 file, 13.075 token; là một request riêng.
  - Các mặt bị loại: bảo mật · trải nghiệm người dùng cuối · tương thích đa nền tảng ·
    an toàn · linh hoạt — không mặt nào bị request chạm tới.
  - Đạt đúng các con số token đã ước (user chọn 1A: đích mềm) — các số 1.290 / 1.320 /
    1.500–2.500 chỉ là tham chiếu, **cấm dùng làm điều kiện PASS/FAIL**.
  - Sửa nội dung luật. Bảy đề xuất chỉ ĐỔI CHỖ, ĐỔI NHÃN, THÊM ngưỡng đếm được và THÊM
    khối định dạng; không đề xuất nào được viết lại một luật đang có.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | đã làm trọn ở request trước (`docs/tdq/research/2026-08-14-toi-uu-llm-workflow.md`, 6 nguồn); không ẩn số bên ngoài mới |
| Vòng scope | BỎ | request trỏ thẳng vào 7 đề xuất đã có sẵn file đích, nội dung nháp và lệnh kiểm — không dấu hiệu nào trong 4 dấu hiệu bật |
| Interview vòng chi tiết | CÓ (xong) | 4 câu, user trả lời `1A 2B 3B 4A 5A` |
| Spec | CÓ | khung bất biến |
| Plan một file, hai phase | CÓ | đúng thứ user chốt: văn bản xanh trước, mã sau |
| Review sâu plan bằng `tdq-reviewer` | CÓ | plan đụng 21 file và đụng chính bộ skill đang chạy — sai một chỗ là hỏng workflow |
| Implement | CÓ | khung bất biến |
| Cổng duyệt giữa phase 1 và phase 2 | CÓ | user chọn 2B — dừng, báo cáo, chờ duyệt rồi mới đụng mã |
| Chia sub-agent để implement song song | BỎ | có phụ thuộc thứ tự (`skill-inventory.md` bị cả hai phase đụng), chạy song song dễ ghi đè |
| QC độc lập bằng `tdq-qc-tester` | CÓ | QC phải đếm lại luật và chạy `pytest` trên bản đã sửa, tách khỏi người sửa |
| Chạy thử bằng model hạng thấp | CÓ | user chọn 3B — bù đúng giới hạn của bằng chứng tĩnh; là hạng mục quan sát, không phải cổng chặn |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Đ2 — Phần C của `tdq-intake/SKILL.md` về reference | `skills/tdq-intake/SKILL.md` · `references/quick-lane.md` | `grep -c "" skills/tdq-intake/SKILL.md` giảm ≥ 20 dòng; `grep -c "^[0-9]\. " references/quick-lane.md` ≥ 9; luật cặp file ≥ 17 |
| 2 | Đ3 — Phần B+C của `tdq-build/SKILL.md` về 2 reference | `skills/tdq-build/SKILL.md` · `references/qc.md` · `references/report-template.md` | `python3 scripts/context_surface.py --quiet` cho thân `tdq-build` < 1.400 token; luật cụm 3 file ≥ 23 |
| 3 | Đ4 — mục thuần giải thích xuống phụ lục, giữ 100% chữ | 3 file `skills/tdq-conventions/references/` | `grep -c "^## Phụ lục" reminder-codes.md` = 1; số từ (`wc -w`) trước = sau ở cả 3 file |
| 4 | Đ5 — 2 dòng mơ hồ thành ngưỡng đếm được | `skills/tdq-intake/references/scope-round.md` | `grep -cEi "phù hợp\|nếu cần\|tối ưu\|hợp lý\|linh hoạt"` = 0 (trước: 2); luật ≥ 8 |
| 5 | Đ6 — khai "nhắc lại có chủ ý" ở 8 chỗ | 8 file `skills/` | `grep -rl "nhắc lại có chủ ý" skills/ \| wc -l` ≥ 8; luật cụm 8 file = 72 |
| 6 | Đ7 — khối định dạng đầu ra cho 3 agent | `agents/tdq-*.md` | `grep -c '^```' agents/<file>.md` ≥ 2 mỗi file; luật cụm 3 file ≥ 6 |
| 7 | Đ1 — cờ lọc cho `skill_inventory.py` | `scripts/skill_inventory.py` | `--loc "workflow" \| wc -c` < mặc định `\| wc -c`; `--tat-ca` cho `diff` rỗng với bản hiện nay |
| 8 | 2 test mới cho Đ1 | `tests/test_skill_inventory.py` | `pytest tests/test_skill_inventory.py -q` xanh; tổng `pytest tests/` ≥ 565 passed |
| 9 | 2 reference đổi dòng lệnh gọi | `references/analyze-full.md` · `references/skill-inventory.md` | cả hai chứa `--loc`; luật mỗi file ≥ 5 / ≥ 4 |
| 10 | Bảng đối chiếu luật trước/sau, 10 dòng | `docs/tdq/qc/2026-08-14-ap-goi-day-du.md` | đủ 10 dòng, 0 dòng có "sau" < "trước" |
| 11 | Báo cáo chạy thử model hạng thấp | mục trong file QC | có kết luận: bộ skill mới có bị bỏ bước nào không, kèm bước bị bỏ nếu có |
| 12 | Report cuối | `docs/tdq/reports/2026-08-14-ap-goi-day-du.md` | 10–20 dòng, có số token trước/sau và số luật trước/sau |

## 3. Cách tiếp cận & lý do

- Chọn: áp từng đề xuất một, mỗi đề xuất là một task riêng có phép kiểm riêng, theo đúng
  thứ tự Đ2 → Đ3 → Đ4 → Đ5 → Đ6 → Đ7 → (cổng duyệt) → Đ1 → 2 test → đổi 2 dòng lệnh gọi.
  Mỗi task chạy `pytest tests/ -q` và `doc_lint.py` ngay sau khi sửa.
- Vì:
  - Bảy đề xuất đã có sẵn nội dung nháp và lệnh kiểm trong knowledge doc — công việc là
    thi hành, không phải thiết kế lại; tách từng task giữ được `git diff` nhỏ, hỏng chỗ
    nào lùi đúng chỗ đó.
  - Thứ tự Đ6 trước Đ1 là bắt buộc: `references/skill-inventory.md` bị **cả hai** đề xuất
    đụng (Đ6 dán chú nguồn gốc, Đ1 đổi dòng lệnh). Làm ngược lại sẽ ghi đè.
  - Đ4 giữ nguyên 100% câu chữ (user chọn 4A), nên phép kiểm của nó là `wc -w` bằng nhau —
    một phép kiểm mạnh hơn hẳn đếm mệnh lệnh.
- Đã loại:
  - Gói vừa (bỏ Đ1 và Đ4) — vì user đã chốt Gói đầy đủ sau khi biết Đ1 là khoản tiết kiệm
    lớn nhất (≈ 7.000 token/lần analyze).
  - Chia sub-agent implement song song — vì phụ thuộc thứ tự nói trên.
  - Đặt đích token cứng — user chọn 1A; đích cứng xung đột với luật "tuân thủ thắng khi
    xung đột" đã kế thừa từ request trước.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG. Kiểm kê 2026-08-14: 284 skill
trên đĩa.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | phase Đ1: tra ai gọi `skill_inventory.py` trước khi thêm cờ; `extract . --code-only` cuối turn có đổi mã |
| mem0-memory | user | DÙNG | search trước khi chốt cách làm Đ1; ghi 1 fact sau khi áp xong |
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng là đối tượng bị sửa |
| tavily-search, tavily-research, tavily-cli, tavily-extract, tavily-crawl, tavily-map, tavily-dynamic-search, tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực |
| Đã xét 268 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — task mã duy nhất (Đ1) chỉ thêm một cờ cho script CLI in ra stdout rồi
  thoát, không có tiến trình chạy nền để log. Thay vào đó bắt buộc: khi lọc, dòng cuối
  output phải báo đã ẩn bao nhiêu skill và nêu đúng lệnh xem đủ.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Hai test mới của Đ1 chạy được bằng một lệnh: một test cho cờ lọc, một test giữ nguyên
  hành vi mặc định (không cờ = output y như hiện nay).
- Không luật nào biến mất; xung đột giữa cắt token và độ tuân thủ → **tuân thủ thắng**.
- Không commit, không push khi user chưa yêu cầu.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sửa chính bộ skill đang chạy — hỏng một file là hỏng request kế tiếp | cao | mỗi đề xuất một task, chạy `doc_lint.py` + `pytest tests/ -q` ngay sau task; `git diff` giữ nhỏ theo từng Đ |
| Đ1 lọc mất một năng lực đáng dùng ở bước B0 | cao | dòng cuối bắt buộc báo số skill bị ẩn + lệnh `--tat-ca`; luôn in đủ nguồn `project` và `plugin:tdq-workflow`; 1 test cho hành vi mặc định |
| `references/skill-inventory.md` bị cả hai phase đụng | trung bình | thứ tự cố định trong plan: Đ6 ở phase 1, dòng lệnh ở phase 2; QC đối chiếu cả hai thay đổi còn nguyên |
| Đếm mệnh lệnh bằng regex báo sai khi văn bản đổi chỗ | trung bình | đếm theo **cụm file** đúng như bảng `## Đối chiếu luật`, không đếm từng file rời |
| Chạy thử bằng model hạng thấp cho kết quả ngẫu nhiên | thấp | là hạng mục QC quan sát, ghi nguyên kết quả; không dùng làm điều kiện chặn |
| Hook `edit_gate` chặn khi plan không có đúng một `[~]` | thấp | mỗi task đánh `[~]` trước khi sửa, `[x]` ngay khi kiểm xanh; cấm gom tick |
| Không cần model/download/cài đặt gì | — | Đ1 dùng thư viện chuẩn Python, không thêm gói |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Đ2 chuyển đúng chỗ | `grep -c "" skills/tdq-intake/SKILL.md` · `grep -c "^[0-9]\. " skills/tdq-intake/references/quick-lane.md` | giảm ≥ 20 dòng · ≥ 9 bước |
| Q2 | Đ3 chuyển đúng chỗ | `python3 scripts/context_surface.py --quiet \| grep "tdq-build/SKILL.md"` | thân < 1.400 token |
| Q3 | Đ4 giữ 100% câu chữ | `wc -w` 3 file trước/sau · `grep -c "^## Phụ lục" reminder-codes.md` | số từ bằng nhau · = 1 |
| Q4 | Đ5 hết từ mơ hồ | `grep -cEi "phù hợp\|nếu cần\|tối ưu\|hợp lý\|linh hoạt" skills/tdq-intake/references/scope-round.md` | = 0 |
| Q5 | Đ6 khai đủ 8 chỗ | `grep -rl "nhắc lại có chủ ý" skills/ \| wc -l` | ≥ 8 |
| Q6 | Đ7 có khối định dạng | `grep -c '^```' agents/tdq-implementer.md agents/tdq-qc-tester.md agents/tdq-reviewer.md` | ≥ 2 mỗi file |
| Q7 | Đ1 lọc thật sự nhỏ hơn | `python3 scripts/skill_inventory.py --loc "workflow" \| wc -c` vs không cờ | nhỏ hơn |
| Q8 | Đ1 giữ nguyên hành vi mặc định | `diff <(python3 scripts/skill_inventory.py) <bản lưu trước khi sửa>` | rỗng |
| Q9 | Đ1 có đường xem đủ | chạy `--loc` rồi đọc dòng cuối | có số skill bị ẩn + đúng lệnh `--tat-ca` |
| Q10 | 2 test mới xanh, không hồi quy | `python3 -m pytest tests/ -q` | ≥ 565 passed, 0 failed |
| Q11 | Bảng đối chiếu luật | `grep -cEi "cấm\|bắt buộc\|phải \|không được\|luôn \|dừng\|ngay"` theo từng cụm file của bảng gốc | đủ 10 dòng, 0 dòng "sau" < "trước" |
| Q12 | Token tầng nạp giảm | `python3 scripts/context_surface.py --quiet` trước/sau | tổng tầng `nạp khi gọi skill` giảm (không đặt ngưỡng số — đích mềm 1A) |
| Q13 | Không lọt phạm vi | `git status --porcelain -- hooks portable` | rỗng |
| Q14 | Bộ tài liệu hợp lệ | `python3 scripts/doc_lint.py` trên spec + plan | exit 0 |
| Q15 | Chạy thử model hạng thấp | sub-agent model rẻ làm một request nhỏ theo bộ skill mới | có kết luận ghi rõ bước nào bị bỏ, hoặc "không bỏ bước nào" |

DoD:

- Cả 15 hạng mục QC có bằng chứng ghi trong `docs/tdq/qc/2026-08-14-ap-goi-day-du.md`;
  Q1–Q14 PASS, Q15 có kết luận (không dùng làm cổng chặn).
- Bảy đề xuất Đ1–Đ7 đều đã áp, mỗi đề xuất có ít nhất một dòng bằng chứng.
- Phase 1 đã qua cổng duyệt của user trước khi phase 2 bắt đầu.
- `pytest tests/ -q` xanh, `hooks/` và `portable/` không có thay đổi nào.
- Report 10–20 dòng đã viết, không commit, không push.

## 7. Câu hỏi còn mở

(rỗng)
