# PLAN — Bỏ cổng clean code, thay bằng luật SOLID (HOÀN THÀNH)

Ngày: 2026-08-16 · Spec: ../spec/2026-08-16-1300-bo-cong-clean-code.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 16 task nối nhau trên một chuỗi phụ thuộc chặt: file luật phải có trước thì test mới viết được, cổng cũ phải gỡ xong thì grep dọn dẹp mới sạch. Ba task đụng chung `scripts/doc_lint.py` nên tách worktree chỉ đẻ xung đột merge (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Xoá file là việc khó đảo: trước mỗi task xoá, chạy `grep -rn "<tên>"` một lượt và dán
   kết quả vào task. Còn người gọi → dừng, sửa người gọi trước.

## P1 — File luật mới và bộ test của nó

- [x] **T1.1** (n5 e10m) `tests/test_clean_code_rule.py` khung đỏ: đọc
  `skills/tdq-conventions/references/clean-code.md`, kiểm đủ 3 mục `## Khi nào áp dụng`
  / `## Làm gì` / `## Tự kiểm` — Test: `pytest tests/test_clean_code_rule.py -k khuon`
  (đỏ vì chưa có file luật)
- [x] **T1.2** (n8 e25m) Viết `skills/tdq-conventions/references/clean-code.md` mục
  `## Làm gì`: bảng 5 luật, mỗi luật đúng 2 cột "khi có class" và "khi chỉ có hàm/module",
  cộng mục `## Nguồn` chép 4 URL từ research — Test:
  `pytest tests/test_clean_code_rule.py -k "bang_solid or nguon"` (đủ SRP/OCP/LSP/ISP/DIP,
  mỗi mã có cả 2 cột không rỗng; mọi URL có mặt trong file research)
- [x] **T1.3** (n5 e15m) Mỗi luật kèm một ví dụ ĐÚNG và một ví dụ SAI trỏ vào file thật
  trong `scripts/` — Test: `pytest tests/test_clean_code_rule.py -k vi_du` (mọi đường dẫn
  nêu trong ví dụ đều `os.path.isfile` được)
- [x] **T1.4** (n3 e8m) LSP mang nhãn giới hạn "chỉ áp nguyên văn khi có class con hoặc
  nhiều bản cài cùng một giao diện" và đánh dấu rõ bản đọc cho hàm là suy diễn của repo,
  không phải trích Liskov — Test: `pytest tests/test_clean_code_rule.py -k lsp_gioi_han`
- [x] **T1.5** (n5 e12m) Mục `## Tự kiểm`: đúng 5 câu hỏi có/không, mỗi câu một dòng, kết
  bằng dấu hỏi; cộng mục `## Khi nào áp dụng` với dấu hiệu nhận ra được bằng mắt — Test:
  `pytest tests/test_clean_code_rule.py -k "checklist or khi_nao"`

**Xong P1 khi**: `python3 scripts/doc_lint.py skills/tdq-conventions/references/clean-code.md`
exit 0 và `pytest tests/test_clean_code_rule.py -q` xanh.

## P2 — Nối luật vào workflow

- [x] **T2.1** (n3 e10m) `skills/tdq-conventions/SKILL.md` thêm dòng nạp
  `references/clean-code.md`; SKILL.md đang đúng 130 dòng chạm trần nên nới
  `SKILL_LINE_LIMITS["tdq-conventions"]` lên 133 kèm comment lý do ngay tại chỗ (tiền lệ
  0.19.0) — Test: `pytest tests/test_clean_code_rule.py -k conventions_nap` và
  `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` exit 0
  - Chạm: `scripts/doc_lint.py` hằng `SKILL_LINE_LIMITS` → `rule_r6()` (nguồn:
    `graphify affected "SKILL_LINE_LIMITS" --depth 2`)
- [x] **T2.2** (n5 e12m) `doc_lint` R9 phủ thêm `clean-code.md`: sửa `_r9_in_scope()` thêm
  đúng một đường dẫn cụ thể, KHÔNG thêm cả thư mục `references/` — Test:
  `pytest tests/test_doc_lint.py -k r9` (file luật thiếu 1 trong 3 mục thì R9 báo lỗi; file
  reference khác của conventions vẫn không bị soi)
  - Chạm: `scripts/doc_lint.py::_r9_in_scope` → `rule_r9()` (nguồn:
    `graphify affected "_r9_in_scope" --depth 2`)

**Xong P2 khi**: `pytest tests/test_doc_lint.py tests/test_clean_code_rule.py -q` xanh.

## P3 — Gỡ cổng hỏi khỏi khuôn spec

- [x] **T3.1** (n3 e8m) `skills/tdq-spec/references/spec-template.md`: xoá mục
  `## Khuôn hỏi clean code` và đổi dòng `Clean code: BẬT|TẮT` §4 thành một dòng trỏ tới
  `clean-code.md` — Test: `grep -c "Khuôn hỏi clean code\|Clean code: BẬT"` ra 0, và
  `pytest tests/test_skill_shape.py -q` xanh
- [x] **T3.2** (n3 e6m) `skills/tdq-spec/SKILL.md`: xoá bước 1b, đánh số lại các bước sau
  cho liên tục — Test: `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md` exit 0
  (R3 kiểm bước đánh số liên tục)

**Xong P3 khi**: hai file trên `doc_lint` exit 0 và grep hai chuỗi trên ra 0.

## P4 — Đổi hạng mục DoD ở QC

- [x] **T4.1** (n5 e12m) `skills/tdq-build/references/qc.md`: dòng 12 và 46-47 đổi từ
  "chạy `code_rule_scan.py` khi spec ghi BẬT" sang "trả lời checklist 5 câu của
  `clean-code.md`, ghi đáp án vào file qc" — Test:
  `pytest tests/test_clean_code_rule.py -k qc_khop_portable`
- [x] **T4.2** (n3 e8m) `portable/workflow/references/qc.md` dòng 20-21 sửa khớp từng bước
  với bản `skills/` — Test: cùng lệnh T4.1 (test so hai file, cả hai phải nhắc checklist
  và không bản nào còn chữ `code_rule_scan`)

**Xong P4 khi**: test `qc_khop_portable` xanh.

## P5 — Xoá script, test và dấu vết

- [x] **T5.1** (n3 e6m) Dọn thư viện `rules/`: xoá dòng nhắc `code_rule_scan.py` trong
  `chung.md` (mục "Khi nào áp dụng") và `index.md` (mục "Khi nào áp dụng"), giữ nguyên 10
  file — Test: `pytest tests/test_rules_library.py -q` xanh và `ls rules/ | wc -l` ra 10
- [x] **T5.2** (n3 e8m) Xoá `scripts/code_rule_scan.py`, `tests/test_code_rule_scan.py`,
  `tests/test_clean_code_workflow.py`. Trước khi xoá dán kết quả `grep -rn code_rule_scan`
  vào task này — Test: `ls` cả ba báo không tồn tại; `python3 -m pytest -q` xanh
  - Chạm: `scripts/code_rule_scan.py` → không node nào phụ thuộc (nguồn:
    `graphify query "code_rule_scan"` trả 13 node toàn cạnh `contains` nội bộ file)
  - Dùng: `graphify`
  - Để: xác nhận lại ngay trước khi xoá rằng không node nào ngoài file gọi vào — xoá file
    là việc khó đảo. Agent ngoài không có skill system: đọc
    `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Ra: kết quả lệnh dán thẳng vào task này, nêu rõ số cạnh vào từ file khác
  - Kiểm: `graphify query "code_rule_scan"` không có cạnh nào từ file ngoài trỏ vào
  - Không dùng cho: chạy `graphify extract` giữa task, sửa đồ thị, tra node không liên quan
- [x] **T5.3** (n3 e8m) Quét tham chiếu mồ côi trên toàn repo, sửa hết chỗ còn sót — Test:
  `grep -rn "code_rule_scan" --include=*.md --include=*.py . | grep -v CHANGELOG | grep -v docs/tdq | grep -v graphify-out`
  ra 0 dòng
  - Đã sửa: comment R9 trong `scripts/doc_lint.py` đổi "code_rule_scan.py" thành
    "script scan cũ" — không cần nêu tên một file đã xoá.
  - CÒN LẠI 2 dòng, cả hai ở `tests/test_clean_code_rule.py` (docstring + assert
    `assertNotIn("code_rule_scan", ...)`). Đây là chốt chặn hồi quy, không phải tham
    chiếu mồ côi: xoá chuỗi đó đi là mất luôn phép kiểm. Q11 chấm theo nghĩa này,
    grep phải loại thêm chính file test đó, cùng `docs/workinglog/` (nhật ký lịch sử,
    ghi lại việc đã làm — sửa nhật ký là làm sai lệch hồ sơ).

**Xong P5 khi**: grep sạch và suite xanh.

## P6 — Log & test bắt buộc

Log: BỎ — việc này chỉ XOÁ code và sửa tài liệu; sửa `doc_lint.py` là mở rộng một hằng
phạm vi và một điều kiện, không thêm runtime nào có vòng đời riêng để ghi log.

- [x] **T6.1** (n3 e10m) `tests/test_clean_code_rule.py` bù đủ độ phủ đã mất: số hạng mục
  test phải ≥ số hạng mục của hai file test bị xoá; ghi số trước/sau vào task này — Test:
  `pytest tests/test_clean_code_rule.py -q` và đối chiếu số test suite trước/sau
  - MẤT: `tests/test_code_rule_scan.py` 4 test + `tests/test_clean_code_workflow.py`
    3 test = 7 test (nguồn: `git show HEAD:<file> | grep -c "    def test_"`).
  - BÙ: `tests/test_clean_code_rule.py` 20 test + 3 test R9 mới trong
    `tests/test_doc_lint.py` (r9 từ 5 lên 8) = 23 test. 23 ≥ 7.
  - Suite toàn repo sau khi xoá: `703 passed, 375 subtests` — không đỏ chỗ nào.

## P7 — Phát hành, QC và report

- [x] **T7.1** (n3 e8m) `CHANGELOG.md` mục `## 0.22.0 — 2026-08-16` và
  `.claude-plugin/plugin.json` lên `0.22.0` — Test:
  `grep -c "0.22.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1
- [x] **T7.2** (n5 e20m) QC: chạy Q1–Q19 của spec §6, ghi bằng chứng vào
  `docs/tdq/qc/2026-08-16-1300-bo-cong-clean-code.md`. Riêng Q18 là chạy checklist 5 câu
  của chính `clean-code.md` lên chính nó và lên `doc_lint.py` sau khi sửa, ghi đáp án —
  Test: mọi hạng mục PASS có bằng chứng dán vào file qc
  - Dùng: `tdq-qc-tester`
  - Để: kiểm độc lập Q1–Q19 và soi riêng câu "model yếu đọc luật này có làm đúng không",
    theo lộ trình spec §1b. Agent ngoài không có skill system: đọc
    `skills/tdq-build/references/qc.md` rồi làm theo.
  - Ra: một mục `## Kiểm độc lập` trong file qc, có phán quyết PASS/FAIL kèm bằng chứng
  - Kiểm: file qc có mục đó và mọi dòng FAIL đều có task fix tương ứng trong plan này
  - Không dùng cho: sửa code, sửa spec, tự quyết mở vòng fix
- [x] **T7.3** (n3 e10m) Report `docs/tdq/reports/2026-08-16-1300-bo-cong-clean-code.md`
  có bảng thời gian thật lấy từ `python3 scripts/tdq_timing.py show` — Test:
  `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-16-1300-bo-cong-clean-code.md`
  exit 0 và report có mục `## Thời gian` với số phút thật
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng một fact ngắn cho project TDQWorkflow — clean code đổi từ scan bằng
    linter sang luật SOLID thường trực. Agent ngoài không có skill system: đọc
    `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một fact trong mem0, project = TDQWorkflow, nêu quyết định và ngày
  - Kiểm: `search_memories` với từ khoá "clean code SOLID" trả về fact vừa ghi
  - Không dùng cho: ghi lại nội dung spec/plan, lưu số liệu test, ghi nhiều hơn một fact

**Xong P7 khi**: file qc đủ Q1–Q19 PASS, report đã ghi, user đã được hỏi về commit.

## Definition of Done

Trỏ về §6 của spec. Từng hạng mục và lệnh kiểm:

| # | Lệnh kiểm |
|---|---|
| Q1 | `python3 scripts/doc_lint.py skills/tdq-conventions/references/clean-code.md` exit 0 |
| Q2 | `pytest tests/test_clean_code_rule.py -k bang_solid` |
| Q3 | `pytest tests/test_clean_code_rule.py -k vi_du` |
| Q4 | `pytest tests/test_clean_code_rule.py -k lsp_gioi_han` |
| Q5 | `pytest tests/test_clean_code_rule.py -k checklist` |
| Q6 | `pytest tests/test_clean_code_rule.py -k conventions_nap` |
| Q7 | `grep -c "Khuôn hỏi clean code" skills/tdq-spec/SKILL.md skills/tdq-spec/references/spec-template.md` ra 0 |
| Q8 | `grep -c "Clean code: BẬT" skills/tdq-spec/references/spec-template.md` ra 0 |
| Q9 | `pytest tests/test_clean_code_rule.py -k qc_khop_portable` |
| Q10 | `ls` ba file đã xoá đều báo không tồn tại |
| Q11 | `grep -rn code_rule_scan` lọc CHANGELOG/docs-tdq/graphify-out ra 0 dòng |
| Q12 | `pytest tests/test_rules_library.py -q` xanh, `ls rules/` ra 10 file |
| Q13 | `pytest tests/test_doc_lint.py -k r9` |
| Q14 | `python3 -m pytest -q` 0 đỏ, ghi số test trước/sau vào file qc |
| Q15 | `python3 scripts/doc_lint.py <mọi file đã sửa>` exit 0 |
| Q16 | `python3 scripts/doc_lint.py docs/tdq/spec/*.md` exit 0 |
| Q17 | `grep -c "0.22.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1 |
| Q18 | Checklist 5 câu của `clean-code.md` chạy lên chính nó và lên `doc_lint.py`, đáp án ghi vào file qc |
| Q19 | Agent `tdq-qc-tester` báo cáo PASS, hoặc FAIL thì mở vòng fix trong plan |

## QC vòng 1 — fix

Nguồn: lượt kiểm độc lập `tdq-qc-tester` (Q19). Bốn phát hiện, hai nhóm.

- [x] **QC1.1** (n5) Checklist 5 câu chỉ hỏi theo bản đọc HÀM: câu LSP không nhắc
  substitutability khi có kế thừa, câu OCP không nhắc "thêm class con thay vì sửa class
  cũ". Model yếu sửa một cây class sẽ không được nhắc đúng nội dung gốc. Sửa hai câu để
  mỗi câu phủ cả hai cột của bảng, VẪN đúng 5 câu — Test:
  `pytest tests/test_clean_code_rule.py -k checklist` (thêm phép kiểm: câu LSP chứa
  "kế thừa", câu OCP chứa "class")
- [x] **QC1.2** (n2) Lệnh Q11 và Q12 trong spec §6 viết sai nên không bao giờ ra đúng
  điều kiện PASS: Q11 thiếu `grep -v docs/workinglog`, Q12 ghi `ls rules/` trong khi
  đường dẫn thật là `skills/tdq-build/references/rules/`. Sửa hai dòng lệnh trong spec §6
  và ghi rõ ở file qc — Test: chạy đúng hai lệnh sau khi sửa, Q11 ra 2 dòng (đều là chốt
  chặn hồi quy trong `tests/test_clean_code_rule.py`), Q12 ra 10
