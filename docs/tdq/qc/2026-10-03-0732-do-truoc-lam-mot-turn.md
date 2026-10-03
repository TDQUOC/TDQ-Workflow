# QC — Đo trước ở spec, implement chạy hết plan trong một lượt

Ngày: 2026-10-03 · Plan: ../plan/2026-10-03-0732-do-truoc-lam-mot-turn.md · Vòng: 1 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết luận: PASS, có 1 lệch spec chờ duyệt.** Q1–Q16 PASS; Q17 PARTIAL (macOS/Linux tắt). Đây là
request đầu tiên tự áp luật nó vừa xây: một ngưỡng của DoD trượt được ghi bằng `lech add` thay vì
dừng giữa implement để hỏi.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | R14 bắt ngưỡng thiếu đo | `discover -p test_doc_lint_r14.py -k bat` | `Ran 8 tests OK` | PASS |
| Q2 | R14 im khi đủ cột | `… -k du_cot` | `Ran 3 tests OK` | PASS |
| Q3 | R14 không bắt phép tồn tại | `… -k ton_tai` | `Ran 2 tests OK` | PASS |
| Q4 | R14 không hồi tố | `doc_lint.py docs/tdq/spec` | 0 dòng `[R14]` trên 103 spec cũ | PASS |
| Q5 | Độ chính xác trên spec thật | `… -k chinh_xac` | `Ran 6 tests OK` — 10/10 hàng có ngưỡng, 0/10 hàng không ngưỡng | PASS |
| Q6 | `approve spec` từ chối | `discover -p test_approve_do_truoc.py -k tu_choi` | `Ran 5 tests OK` | PASS |
| Q7 | Lối thoát có lý do | `… -k bo_qua` | `Ran 6 tests OK` | PASS |
| Q8 | Vòng đời lệch | `discover -p test_lech_spec.py` | `Ran 27 tests OK` | PASS |
| Q9 | `pause` phân loại | `discover -p test_implement_pause.py` | `Ran 11 tests OK` | PASS |
| Q10 | Hook nhắc | `discover -p test_ask_gate.py` | `Ran 10 tests OK` | PASS |
| Q11 | Lời chặn Stop | `-p test_stop_gate.py` + `-p test_agy_hooks.py` | `Ran 104 OK` · `Ran 26 OK` | PASS |
| Q12 | Luật dừng | `discover -p test_luat_dung.py -k dung` | `Ran 9 tests OK` | PASS |
| Q13 | QC/report thấy lệch | `-p test_lech_spec.py -k next` + `-p test_luat_dung.py -k qc_report` | `Ran 9 OK` · `Ran 2 OK` | PASS |
| Q14 | Kiến trúc | `grep "2026-10-03 (yêu cầu 0732)" docs/kien-truc.md` + `-p test_common.py` + `grep -rn "^import hooks\|^from hooks" scripts` | 1 dòng · `Ran 10 OK` · 0 import | PASS |
| Q15 | Trần token | `token_budget.py --kiem` | exit 0; lớn nhất `qc.md` 3.203/3.500 | PASS |
| Q16 | Trọn bộ test | `python -m unittest discover tests` | `Ran 2425 tests in 351.188s · OK (skipped=9)` | PASS |
| Q17 | Ba hệ | trọn bộ trên Windows; ping hai máy | Windows OK; `100.105.75.71` và `100.67.252.79` không trả lời | PARTIAL |

## Bằng chứng

### Q15 — đo trước so với đo sau

| File | Đo trước (spec §6) | Sau | Phần thêm |
|---|---|---|---|
| `qc.md` | 2.959 | 3.203 | +244 |
| `report-template.md` | 1.901 | 2.070 | +169 |
| `phases.md` | 1.792 | 1.841 | +49 |
| `reminder-codes.md` | 1.389 | 1.469 | +80 |
| `spec-template.md` | 2.512 | 2.615 | +103 |
| `spec-template-huong-dan.md` | 1.035 | 1.404 | **+369** |

Ước lượng trong spec là "≤ 300 token/file". `spec-template-huong-dan.md` vượt ước lượng (+369)
nhưng ngưỡng thật của Q15 là trần 3.500 — vẫn còn cách 2.096. Ước lượng sai, ngưỡng không trượt:
ghi ở đây, không thành lệch.

### Trọn bộ test, lần đỏ trước khi xanh

Lần chạy thứ nhất `Ran 2422 · FAILED (failures=1)`: `test_luat_gate_chat` — tên tool popup chỉ được
xuất hiện ở hai file viết luật, mà `tdq-build/SKILL.md` và `reminder-codes.md` vừa gọi tên nó. Đổi
cách diễn đạt ("a question popup"), chạy lại `Ran 2425 · OK`.

## Lệch spec chờ duyệt

`tdq_state.py lech list`:

- **#1 · Q4 / DoD "doc_lint xanh trên chính spec này"** — đo được: R14 bắt Q1 và Q2 của spec này
  (dòng 143–144), vì hai hàng đó trích ví dụ `≤ 200 MB` trong backtick làm dữ liệu test, và T1.2
  đã đóng lỗ "bỏ qua chữ trong backtick" (lỗ đó cho phép lách R14). Phương án đã áp: giữ spec
  nguyên; user duyệt lệch thì điền hai ô `Đo trước`/`Dự phòng` của Q1, Q2 (ghi rõ "ví dụ đầu vào
  của test, không phải ngưỡng sản phẩm"). Lý do: sửa §6 sau khi duyệt làm lệch sha256 và hệ thống
  đòi duyệt lại spec giữa implement — đúng kiểu dừng request này bỏ.

## T5.3 — soát lỗi đúng-sai (`code-review`, mức high)

| # | Phát hiện | Phán quyết | Đã làm gì |
|---|---|---|---|
| 1 | R14 chỉ nhận tên cột tiếng Việt → spec tiếng Anh (`doc_lang=en`) bị `approve spec` chặn oan | NHẬN — lỗi thật | Bí danh tiếng Anh cho 3 cột (`PASS condition`, `Measured before`, `Fallback`); 2 test `NgonNguKhac` |
| 2 | R14 bắt ví dụ trong backtick ở Q1/Q2 của chính spec này | NHẬN là sự thật, KHÔNG sửa mã | Đóng lỗ backtick là có chủ đích (T1.2); ghi thành lệch #1 |
| 3 | `lech duyet/bac --json` in dòng "note … overriding" ra stdout trước JSON | NHẬN — lỗi thật | Dòng ghi chú sang stderr; test `TestJsonSach` |
| 4 | Không chạy được test theo kiểu `tests.<tên>` (5 lỗi import) | BÁC | Repo chạy test bằng `discover` — `tests/` cố ý không là package (ghi ở plan) |

## T5.4 — rút gọn (`simplify`, 4 agent)

Sửa, không đổi hành vi (10 module test vùng chạm xanh trước và sau):

- `_common.remind()` thêm `decide=False`; `ask_gate.py` thôi chép lại khử trùng + sổ lượt + dựng
  JSON, và nhờ đó có luôn bước đổi đường dẫn tuyệt đối mà bản chép đã bỏ sót.
- Danh sách 4 loại dừng trong lời nhắc lấy từ `LOAI_DUNG` — một nguồn thay vì ba.
- `_flag_pairs` dùng chung cho `pause` và `lech` thay hai vòng lặp gần giống nhau.
- `LECH_QUYET` từ dict tự trỏ chính nó thành tuple.
- R14 tra chỉ số cột một lần mỗi bảng; kiểm mốc ngày chỉ còn ở `r14_loi`.

Bỏ qua có lý do: `Doc.from_text` và bộ tách ô dùng chung với R8, hàm mốc chung với R11 (chạm luật
cũ ngoài diff) · đọc spec một lần khi duyệt (đổi chữ ký hàm băm, lợi một lần đọc file) · tối ưu
vi mô trong `render_next`.

## Nợ khai ra, không giấu

1. **Q17 — macOS và Linux chưa chạy.** Hai máy tắt (kiểm lại lúc 10:35).
2. **Cổng Stop chưa biết lệch chờ duyệt.** Report hỏi duyệt là luật + dòng `next`, chưa có máy
   chặn kết request khi còn lệch `cho`. Reviewer `simplify` (góc altitude) đề xuất đưa vào
   `done_when` của phase report; đó là đổi hành vi, để request sau.
3. **Hỏi bằng popup trong chính phiên này.** Phase analyze của request này hỏi user bằng tool
   popup, trong khi luật `user-facing-block.md` cấm popup ở MỌI câu hỏi. Lỗi của agent, không của
   mã; hook mới chỉ nhắc ở implement/qc nên không bắt được ca này.
4. **Codex không có hook nhắc tương đương** (Codex không có tool popup) — chỉ có luật trong skill.
