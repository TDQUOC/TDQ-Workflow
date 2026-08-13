# REPORT — Trình bày lại full chat sau khi bị hook chặn

Ngày: 2026-08-13 · Lane: full · Mode: main · Spec/Plan/QC: cùng slug trong `docs/tdq/`.

**Vấn đề.** Focus mode chỉ hiện message CUỐI mỗi lượt. `stop_gate.py` là hook Stop, chặn SAU
khi model đã in khối chat có câu hỏi, nên khối đó bị gộp vào `N messages hidden` — user chỉ
thấy "trả lời A hoặc B" mà không thấy A, B là gì.

**Đã làm.**
- `hooks/scripts/stop_gate.py`: hai lời chặn `[TDQ:LOG]` và `[TDQ:TICK]` nay ra lệnh in LẠI
  NGUYÊN VĂN khối chat cuối. `[TDQ:LOG]` bỏ câu bảo tự thêm mục `## HH:MM` (mâu thuẫn luật cấm
  sửa tay working log), thay bằng lệnh `tdq_finish.py`. Sửa kèm lỗi tiềm ẩn: `culprit` lấy từ
  sổ turn không cắt theo `MAX_PATH_CHARS` nên path dài làm lời chặn vượt trần 300 ký tự.
- `skills/tdq-conventions/SKILL.md` §1 thêm mục 5: turn còn chạy tiếp sau khi đã in khối
  user-facing (hook chặn, sót việc, lỗi tool) → message cuối in lại nguyên văn 100% khối đó,
  ngay sau dòng `✓ [TDQ:<MÃ>]`. Áp cho MỌI trường hợp, không riêng hook. Tách phần ảnh working
  log ra `references/worklog-images.md` để file còn 118 dòng (trần R6 là 120).
- `tests/test_stop_gate.py`: lớp `TestStopGateReprint` — 4 test giữ cụm bắt buộc và trần 300 ký tự.

**QC.** 5/5 PASS, không vòng fix. Full suite: 503 passed, 178 subtests passed.
**Còn lại.** Luật in lại là luật viết, không có máy ép. Chưa commit lần nào trong request này.
