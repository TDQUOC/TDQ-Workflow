# QC — Gate hỏi trong chat & Next step nêu pha kế
Ngày: 2026-09-03 · Plan: ../plan/2026-09-03-1220-gate-chat-va-next-pha.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Luật cấm popup ở tầng conventions, áp cho mọi câu hỏi | `grep -n "AskUserQuestion" skills/tdq-conventions/references/user-facing-block.md` | dòng 98, kèm chữ "EVERY question" | PASS |
| Q2 | `approval.md` nói rõ hỏi xong kết lượt | `grep -n "kết lượt" skills/tdq-conventions/references/approval.md` | dòng 6, mục `## Hỏi xong là kết lượt` | PASS |
| Q3 | Test khoá cấm popup | `pytest tests/test_luat_gate_chat.py -q -k popup` | 2 passed | PASS |
| Q4 | Mọi dòng `Next step:` nêu pha kế | `pytest tests/test_luat_gate_chat.py -q -k next_step` | 2 passed | PASS |
| Q5 | Test đó đỏ khi xoá tên pha | xoá `phase \`plan\`` khỏi `tdq-spec/SKILL.md` rồi chạy lại Q4 | 1 failed, khôi phục xong xanh lại | PASS |
| Q6 | Luật `Next step:` nói rõ vai trò dự phòng | `grep -n "FALLBACK" skills/tdq-conventions/SKILL.md` | dòng 68, kèm `[TDQ:NEXT]` là đường chính | PASS |
| Q7 | Không còn câu mâu thuẫn về dòng cuối | `grep -c "không viết gì bên dưới" .../user-facing-block.md` | 0 | PASS |
| Q8 | Test khoá luật đường kẻ, khai đúng ký tự | `pytest tests/test_luat_gate_chat.py -q -k duong_ke` | 3 passed | PASS |
| Q9 | Lint tài liệu | `python3 scripts/doc_lint.py skills/ docs/` | exit 1 — 25 phát hiện, TẤT CẢ nằm trong `docs/archive/v0.1/`; 0 phát hiện ngoài archive | PASS có ghi chú |
| Q10 | Không hồi quy | `python3 -m pytest -q` | 100 failed, 1471 passed — đúng mốc 100 | PASS |
| Q11 | Bản portable | `build_portable.py` rồi `tdq_checkportable.py check` ×3 | exit 0; CLEAN 92 / 142 / 85 file | PASS |
| QC-F1 | Toàn suite | `python3 -m pytest -q` | 100 failed, 1471 passed, 1423 subtests passed, 195 s | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | `pytest tests/test_luat_gate_chat.py tests/test_user_facing_block.py tests/test_luat_skill.py tests/test_ranh_gioi.py -q` | 1 failed, 43 passed — đỏ duy nhất là lệch neo có sẵn | PASS có ghi chú |
| QC-F3 | Ràng buộc kiến trúc spec §5 | xem mục bằng chứng | R6 giữ được, `CLAUDE_PLUGIN_ROOT` không lọt bản claude | PASS |
| QC-F4 | Clean code 5 câu | tự soát trên `tests/test_luat_gate_chat.py` | 5/5 "có" | PASS |

## Bằng chứng

### Q9 — exit 1 nhưng không phải lỗi của việc này

```
REMAIN=0        # số phát hiện ngoài docs/archive/
ARCHIVE=25      # số phát hiện trong docs/archive/v0.1/
```

Ba dòng đầu của phần đỏ, đều thuộc một file lưu trữ bản v0.1:

```
docs/archive/v0.1/spec/tdq-workflow-plugin.md:129: [R5] sentence of 50 words (> 40) — split it
docs/archive/v0.1/spec/tdq-workflow-plugin.md:236: [R5] sentence of 48 words (> 40) — split it
docs/archive/v0.1/spec/tdq-workflow-plugin.md:1: [R8] spec missing the section `## 3b. Năng lực & công cụ`
```

`git status` cho thấy việc này không chạm file nào trong `docs/archive/`. Dọn kho lưu trữ
v0.1 là việc ngoài phạm vi spec, nên ghi thành nợ kỹ thuật ở report chứ không sửa ở đây.

### Q10 / QC-F1 — mốc hồi quy

```
100 failed, 1471 passed, 1423 subtests passed in 195.41s (0:03:15)
```

Lần chạy đầu ra 102 đỏ. Hai test dôi ra là `test_user_facing_block.py` — chúng khoá bản luật
CŨ ("mục Năm thành phần", "dòng cuối khối phải là `➤`"), tức chính hai câu mà yêu cầu này cố
tình thay. Đã sửa test theo luật mới, có ghi chú ngày và lý do ngay tại chỗ sửa: mục nhận cả
tên "The six components", và luật 7 bóc đúng một dòng `---` cuối trước khi xét, nên vẫn bắt
được mọi thứ khác lọt xuống dưới khối. Sau đó về đúng 100.

### Q11 — ba bundle

```
portable_claude       CLEAN    92 file(s) match the manifest
portable_codex        CLEAN    142 file(s) match the manifest
antigravity_portable  CLEAN    85 file(s) match the manifest
```

### QC-F2 — vùng chạm

Đỏ duy nhất: `test_luat_skill.py::test_so_dong_ghi_trong_bang_van_tro_dung_cho`, 84/329 dòng
lệch (25,5%, ngưỡng 5%). Con số y hệt mốc trước khi sửa, đã kiểm bằng `git stash`. Lệch có
sẵn của `docs/tdq/audit/luat-hien-co.md`, không do việc này. Mọi node trong các dòng `Chạm:`
đều có test, không có mục `KHÔNG CÓ TEST`.

### QC-F3 — hai ràng buộc kiến trúc của spec §5

1. **R6 giới hạn dòng skill.** `doc_lint.py skills/` exit 0. `tdq-conventions/SKILL.md` chạm
   trần cũ 168 nên trần được nâng lên 177 kèm ghi chú ngày và lý do, đúng lệ file đó đang
   theo. Các skill còn lại không đổi trần; `tdq-intake` từng vọt lên 122/120 và đã nén lại.
2. **Bản claude cấm chữ `CLAUDE_PLUGIN_ROOT`.** `grep -rc` trên `portable_claude/` không ra
   file nào có chuỗi đó, và build in `rewrote 66 plugin-variable use(s), 0 left`.

### QC-F4 — clean code, xét trên file mã duy nhất được thêm

`tests/test_luat_gate_chat.py` là file mã mới duy nhất; ngoài ra chỉ sửa văn bản skill và hai
chỗ trong `tests/test_user_facing_block.py`.

- SRP: có. Ba class test, mỗi class đúng một luật; ba helper mỗi cái một việc.
- OCP: có. Thêm một file được nhắc tên tool chỉ cần thêm một dòng vào `DUOC_NHAC`; thêm một
  pha chỉ cần `PHASE_TABLE` đổi, test đọc thẳng từ đó chứ không chép danh sách pha.
- LSP: có. Mọi nhánh `return` của `cau_next_step` trả cùng kiểu `list[str]`.
- ISP: có. Không tham số nào thừa.
- DIP: có. Tên pha lấy từ `tdq_state.PHASE_TABLE`, nguồn thật, thay vì chép cứng danh sách.

## Kết luận

PASS toàn bộ. Hai mục có ghi chú (Q9, QC-F2) đều là nợ có sẵn từ trước, đã kiểm chứng bằng
`git stash` và bằng `git status`, không phải hồi quy của việc này.
