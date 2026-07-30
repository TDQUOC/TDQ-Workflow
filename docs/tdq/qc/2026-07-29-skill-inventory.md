# QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)

Ngày: 2026-07-29 · Plan: ../plan/2026-07-29-skill-inventory.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest discover tests` | Ran **227** tests — OK (yêu cầu ≥215; 0.3.2: 204) | PASS |
| Q2 | Script trên máy thật | `python3 scripts/skill_inventory.py` | đúng 7 skill (1 user + 6 plugin:tdq-workflow) + 2 dòng nhắc built-in, exit 0 | PASS |
| Q3 | Lọc scope + cache | `python3 -m unittest test_skill_inventory` | 11 test OK (3 tầng settings, scope project khác bị bỏ, 2 version cache chỉ đọc installPath) | PASS |
| Q4 | Log service | settings.json hỏng JSON → chạy script | 1 dòng ⚠️ kèm timestamp, exit 0; `TDQ_LOG=0` → stderr rỗng (2 test) | PASS |
| Q5 | Lint R8 | `python3 -m unittest test_doc_lint` · `doc_lint.py skills portable docs/tdq/spec` | 22 test OK (7 test R8/pair mới); repo thật exit 0 | PASS |
| Q6 | Trần token | `python3 -m unittest test_token_budget test_skill_shape` | OK — intake 86/120 dòng, reference mới 71/200, `next` phase analyze 11/20 dòng | PASS |
| Q7 | Phase table | `python3 -m unittest test_phase_table` | OK — phases.md (skills + portable) sinh lại từ PHASE_TABLE | PASS |
| Q8 | Portable đồng bộ | `python3 -m unittest test_portable_sync test_docs_consistency` | OK | PASS |
| Q9 | Rà bảo mật script | xem "Bằng chứng Q9" | 5 hạng mục rà; 1 phát hiện thật (ANSI escape) → **QC1.1**, đã fix red→green | PASS |
| Q10 | Đọc "chỉ làm theo chữ" | đi từng dòng `references/skill-inventory.md` + khuôn §3b | 1 chỗ trượt (dòng ví dụ trong khuôn copy) → đã sửa thành placeholder + ví dụ tách riêng | PASS |
| Q11 | Đóng gói | `claude plugin validate . --strict` · cài lại | ✔ Validation passed, version 0.3.3; cache chỉ còn bản 0.3.3 mới | PASS |
| Q12 | Không hồi quy hook | `python3 -m unittest test_stop_gate test_turn_snapshot test_e2e_chain` | OK (nằm trong Q1, chạy riêng cũng xanh) | PASS |
| Q13 | Hợp đồng skill khớp | `doc_lint.py --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md` | exit 0 — dogfood trên chính cặp file này | PASS |
| Q14 | Hợp đồng thi hành thật | chạy trường **Kiểm** của khối T9.2 | mục Q9 tồn tại trong file này kèm PASS/FAIL + bằng chứng (artifact trường **Ra**) | PASS |

## Bằng chứng Q9 — rà bảo mật `scripts/skill_inventory.py`

Bối cảnh: skill `security-review` được nạp theo hợp đồng T9.2 nhưng **fail ngay bước nạp
context** — preamble của nó chạy `git diff origin/HEAD...` mà repo không có remote. Lượt rà
vì vậy thực hiện thủ công đúng phạm vi hợp đồng (5 hạng mục), bằng chứng chạy thật:

| Hạng mục | Cách kiểm | Kết quả |
|---|---|---|
| Command injection | `grep subprocess\|os.system\|shell` | không có — script không gọi shell |
| Ghi/xoá file | `grep open(.*w\|unlink\|remove` | không có — chỉ đọc |
| JSON độc (nested 3000 tầng) | chạy script với settings.json `[[[…]]]` | rc 0, không traceback |
| **ANSI escape trong description** | SKILL.md có `\x1b[2J`+`\x07` | **LỌT ra stdout** → QC1.1, fix xong: không còn byte điều khiển |
| Symlink SKILL.md → file ngoài | symlink tới file có dòng `description:` | lộ ≤60 ký tự text (đã lọc escape); chấp nhận — đọc file của chính user, in ra terminal của chính user, không vượt biên trust |

## Lỗi phát hiện trong QC và đã sửa

- **QC1.1 (từ Q9)** — script in nguyên ký tự điều khiển từ SKILL.md ra terminal: một
  SKILL.md xấu xoá/ghi đè được màn hình user. Fix: `_clean()` lọc mọi ký tự < 0x20 khỏi
  name/description. Test `test_control_chars_stripped` red → green; tái diễn 2 kịch bản
  tấn công → cả hai sạch.
- **Q10** — khuôn bảng ghi "copy nguyên khối" nhưng chứa dòng ví dụ dữ liệu thật → model
  yếu sẽ giữ nguyên ví dụ. Fix: khuôn chỉ còn dòng placeholder; ví dụ tách riêng kèm chú
  thích "KHÔNG chép vào bảng thật".

## Ghi chú lệch so với spec (có chủ ý)

1. Spec ghi phán quyết 2 giá trị `DÙNG/KHÔNG`; thực tế thêm **`NỀN`** cho skill khung
   đang chạy (tdq-*) — không có nó thì `--pair` đòi hợp đồng cho chính workflow (vô nghĩa)
   hoặc phải hardcode ngoại lệ tdq-* trong lint (giấu luật vào code). Enum vẫn đóng (3 giá
   trị), R8 kiểm được.
2. Plan T6.1 ghi thêm mục vào `no_state`; thực tế PHASE_TABLE có key `quick` riêng cho lane
   quick → mục mini-plan `Năng lực:` đặt vào `quick` (đúng chỗ hơn, `no_state` giữ nguyên).
3. `doc_lint` khi quét thư mục `spec/` chỉ chạy R8, không áp R1–R7 hồi tố lên spec đã
   duyệt (R1–R7 viết cho doc hướng dẫn skills/portable, không phải tài liệu nghiệp vụ).
4. Q9 chạy thủ công thay vì qua skill `security-review` (skill fail vì repo không có
   remote) — phạm vi và đầu ra đúng theo hợp đồng T9.2, có bằng chứng chạy thật.

## Kết luận

PASS 14/14 ở vòng 1, sau khi sửa QC1.1 (Q9) và khuôn bảng (Q10).
