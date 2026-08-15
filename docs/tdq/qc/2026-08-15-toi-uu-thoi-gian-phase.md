# QC — Tối ưu thời gian xử lý các phase của workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Spec: ../spec/2026-08-15-toi-uu-thoi-gian-phase.md (bản 1.1) · Plan: ../plan/2026-08-15-toi-uu-thoi-gian-phase.md

## Mốc trước

Nguồn: transcript phiên `0a2b58a3` của project `Heineken_AppKetNoi` (131,5 MB), đo ngày
2026-08-15 trong phase analyze. Đây là mốc để so sau khi sửa.

**Đính chính 2026-08-15 (phase implement).** Cách đếm ở bảng dưới đếm theo BẢN GHI jsonl.
Claude Code tách một câu trả lời thành nhiều bản ghi (text một dòng, mỗi tool_use một
dòng) và chép `usage` vào từng bản, nên cách đếm đó vừa thổi phồng số bước vừa luôn cho
ra đúng 1,00 tool call mỗi lượt — kể cả khi model có gộp thật. `step_audit.py` gom theo
`requestId`, đo lại cùng transcript ra: **3.234 bước · 1,03 tool call mỗi lượt (3.085
lượt) · 114 Read lặp · trung vị 4,0 s · p90 12,9 s**. Kết luận không đổi: 1,03 nghĩa là
~97% số lượt chỉ phát đúng một tool call, luật gộp gần như chưa được thi hành. Bảng dưới
giữ nguyên để thấy con số cũ sai ở đâu.

| Chỉ số | Giá trị đo được | Vì sao quan tâm |
|---|---|---|
| Số bước model (API call có usage) | 4.809 | biến chính quyết định tổng thời gian |
| Độ trễ mỗi bước | trung vị 3,3 s · p90 12,3 s | giá của một bước |
| Tổng thời gian model chạy | 7,6 giờ | tác động thực tế lên user |
| Tool call trên mỗi lượt của model | 1,00 (3.095 lượt) | chứng cứ luật gộp chưa từng được thi hành |
| Read lặp lại cùng file | 103 / 278 lượt | bước thừa hoàn toàn bỏ được |
| Lệnh `sleep` (chờ bằng vòng thăm dò) | 30 | mỗi vòng là một bước tròn |
| Context mỗi turn | trung vị 129.709 token · p90 163k | để chứng minh context không phải biến chính |

Quan hệ độ trễ theo context, đo cùng phiên: 80k → 3,0 s · 120k → 3,4 s · 160k → 3,9 s ·
240k → 5,1 s. Context gấp 3 chỉ chậm thêm ~70%, trong khi tổng thời gian tỉ lệ thẳng với
số bước — nên đích của request này là **số bước**, không phải số token.

## Mốc sau

Lệnh: `TDQ_LOG=0 python3 scripts/step_audit.py --sessions 1` (phiên TDQWorkflow đang
build request này) và cùng lệnh với `--transcript-dir` trỏ vào project Heineken.

| Chỉ số | Heineken (mốc trước, đo lại đúng) | Phiên build này | Ghi chú |
|---|---|---|---|
| Số bước model | 3.234 | 2.583 | hai phiên khác việc, không so trực tiếp được |
| Tool call trên mỗi lượt | 1,03 (3.085 lượt) | **1,07** (2.363 lượt) | chỉ số đích của request |
| Read lặp lại cùng file | 114 | 230 | phiên này đọc lại nhiều vì context bị nén 2 lần |
| Độ trễ trung vị | 4,0 s | 4,7 s | giá một bước, không đổi được bằng luật |
| Độ trễ p90 | 12,9 s | 16,9 s | |

**Kết luận:** chỉ số đích là **tool call trên mỗi lượt** — 1,03 trước, 1,07 ở phiên này.
Cả hai đều gần 1,00, nghĩa là luật gộp chưa có tác dụng. Đúng như dự kiến: luật mới nằm
trong `SKILL.md`, chỉ được nạp từ PHIÊN SAU trở đi, nên phiên đang build không thể là
bằng chứng cải thiện — nó là mốc đối chứng. Phép đo thật phải chạy lại lệnh trên sau
một request đầy đủ ở phiên mới; đích chấp nhận được là chỉ số này rời khỏi vùng ~1,0.

## Bảng hạng mục

Ngày: 2026-08-15 · Vòng: 1 · Clean code: TẮT (spec §4) → bỏ hạng mục `code_rule_scan.py`.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Luật một lượt có trong thân SKILL.md | `grep -c "Luật một lượt" skills/tdq-conventions/SKILL.md` | 1 | PASS |
| Q2 | Đủ ba tiêu đề con của khuôn rule | `grep -c "Khi nào áp dụng\|Làm gì\|Tự kiểm" …/SKILL.md` | 3 | PASS |
| Q3 | Nhãn tầng đúng là runtime | `grep -n "tầng 2 — runtime" …/SKILL.md` | dòng 110 | PASS |
| Q4 | Không luật cũ nào mất chữ | `git diff --numstat …/context-budget.md` + `pytest -k luat_cu_con_nguyen` | 54 thêm / 3 xoá — 3 dòng xoá là tiêu đề cũ và câu dẫn, đã viết lại nguyên nghĩa ở mục "Chi phí context (tầng 3)"; 6 gạch đầu dòng luật còn nguyên văn | PASS |
| Q5 | Ba tầng soul không đổi | `git diff --numstat …/soul.md` | 19 thêm / **0 xoá** | PASS |
| Q6 | Bảng cấm gộp đủ 4 ca | `pytest tests/test_step_budget.py -q -k cam_gop` | 1 passed | PASS |
| Q7 | Phần thêm ≤ 900 ký tự | `pytest … -k tran_ky_tu` | 1 passed (thêm 444 ký tự) | PASS |
| Q8 | `--help` của step_audit chạy được | `python3 scripts/step_audit.py --help` | exit 0, đủ 3 cờ | PASS |
| Q9 | Số đo đúng trên transcript mẫu | `pytest … -k step_audit` | 1 passed | PASS |
| Q10 | Log tắt được bằng `TDQ_LOG=0` | `TDQ_LOG=0 python3 scripts/step_audit.py --transcript-dir scripts/samples 2>err >/dev/null; wc -l < err` | 0 dòng stderr (bật mặc định: ≥2 dòng) | PASS |
| Q11 | Project có gạch dưới ra đúng đường dẫn | `pytest … -k token_audit_underscore` | 1 passed | PASS |
| Q12 | Không hồi quy tên project thường | `pytest tests/test_token_audit.py -q` | passed | PASS |
| Q13 | Test file mới xanh | `pytest tests/test_step_budget.py -q` | 12 passed | PASS |
| Q14 | Toàn bộ suite | `python3 -m pytest -q` | **608 passed, 306 subtests** | PASS |
| Q15 | Bản portable đồng bộ | `pytest tests/test_soul_rules.py tests/test_step_budget.py -q` (xem ghi chú) | passed | PASS |
| Q16 | Lint mọi file đã sửa | `python3 scripts/doc_lint.py <10 file>` | exit 0 | PASS |
| Q17 | Luật soul không vỡ | `pytest tests/test_soul_rules.py -q` | passed | PASS |
| Q18 | File QC có hai mốc | `grep -c "^## Mốc" <file này>` | 2 | PASS |
| Q19 | Luật đọc lại là luật MỀM | `pytest … -k doc_lai_mem` | 1 passed — đủ 5 ca bắt buộc đọc lại, có câu "Nghi ngờ thì đọc lại", 0 lần chuỗi "cấm đọc lại" | PASS |
| QC-F1 | Toàn bộ suite bằng lệnh của plan | `python3 -m pytest -q` | 608 passed (trước request: 596) | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | `pytest tests/test_token_audit.py tests/test_skill_shape.py tests/test_skill_inventory.py tests/test_docs_consistency.py -q` | 56 passed, 2 subtests | PASS |
| QC-F3 | Ràng buộc kiến trúc (spec §5) | `ls scripts/step_audit.py` · `grep -c "step_audit.py" …/context-budget.md` · `grep -c "state.json" scripts/step_audit.py` | file mới nằm đúng `scripts/`; skill chỉ nhắc TÊN LỆNH (1 lần), không chép nội dung script; step_audit không đụng `state.json` (0) | PASS |

**Ghi chú Q15 — sửa một dòng DoD.** Plan ghi `pytest tests/test_portable_sync.py`, nhưng
file đó không tồn tại trong repo; chạy sẽ ra "no tests ran" chứ không phải PASS. Phần
đồng bộ `portable/AGENTS.md` thực tế do `tests/test_soul_rules.py` và
`tests/test_step_budget.py` khoá. Đã chạy đúng hai file đó. Đây là lỗi của plan (dòng DoD
trỏ vào lệnh không chạy được), sửa theo luật `qc.md`: làm dòng DoD đo được rồi mới QC.

## Kết luận

PASS toàn bộ 19 hạng mục DoD + QC-F1, QC-F2, QC-F3. Không có hạng mục FAIL, không có vòng
fix. Hai điểm phải nêu trong report: (1) dòng DoD Q15 trỏ sai tên file test, đã sửa; (2)
số đo "1,00 tool call mỗi lượt" ở phase analyze là ảo do đếm theo bản ghi jsonl — số thật
1,03, đã đính chính trong `brief` và mục `## Mốc trước` của file này.
