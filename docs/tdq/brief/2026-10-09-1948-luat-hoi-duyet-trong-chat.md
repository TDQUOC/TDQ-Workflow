# Brief — Luật "hỏi & duyệt trong chat" ghi thẳng vào từng phase
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hi mở request bổ sung instruction vào các phase của tdq workflow là câu hỏi sẽ interface trả lời trong chat như 1a 2b 3c vầ duyệt cũng sẽ date duyệt trong chat ko mở interface câu hỏi chọn

**Đọc lần đầu.**
- Mục tiêu: mọi phase của TDQ khi đặt câu hỏi hay xin duyệt đều in khối hỏi trong chat và kết lượt
  chờ user nhắn (`1a 2b 3c`), KHÔNG mở tool chọn câu hỏi (`AskUserQuestion`).
- Luật này ĐÃ tồn tại, nhưng chỉ ở tầng conventions — nơi phase không đọc tới nếu không mở file:
  · `skills/tdq-conventions/references/user-facing-block.md:99-106` (Hard rules: "Every question is
  asked in chat, never through a popup tool", `AskUserQuestion` banned ở mọi câu hỏi) · quy tắc 8
  về số thứ tự + cặp `1a 2b` · `skills/tdq-intake/references/interview.md:47-48` ·
  `skills/tdq-conventions/references/approval.md` §"Hỏi xong là kết lượt".
- Đo hiện trạng: `grep "AskUserQuestion|popup tool" skills/*/SKILL.md` → **0 kết quả**. Phase chỉ
  nhắc mỗi định dạng option (`tdq-intake/SKILL.md:67`). Hook `hooks/scripts/ask_gate.py` chặn
  nhầm chỗ: chỉ remind (không deny), chỉ chạy ở phase `implement`/`qc`.
- Phạm vi đoán: thêm 1 dòng luật chuẩn vào SKILL.md của các phase có hỏi user (`tdq-spec`,
  `tdq-plan`, `tdq-build`, `tdq-intake` Part C, `tdq-lean`?); cân nhắc đổi `ask_gate.py` từ remind
  sang deny + phủ mọi phase; test chặn trôi luật (`tests/test_skill_docs.py`).
- Chỗ chưa rõ:
  1. Lặp lại toàn văn luật ở từng phase (phạm luật chống lặp `scripts/doc_dup.py`, tốn context) hay
     chỉ 1 dòng ngắn trỏ về luật gốc?
  2. Có đổi hook `ask_gate.py` thành CHẶN (`deny`) call `AskUserQuestion`, hay giữ remind như lựa
     chọn của user ngày 2026-10-03?
  3. Có case thực tế nào vừa dính (phiên nào vừa mở popup hỏi) để làm kịch bản ĐẠT, hay đây là phòng ngừa?
  4. Dải phase nào phải ghi: chỉ 4 phase có câu hỏi, hay mọi SKILL.md?
  5. Có xuất bản luật sang bản devkit/portable (`claude-export`, `devkit/workflow`) cho host khác không?
