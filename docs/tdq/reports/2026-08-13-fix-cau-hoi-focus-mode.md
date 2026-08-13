# Report — Fix: câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-cau-hoi-focus-mode.md · Plan: ../plan/2026-08-13-fix-cau-hoi-focus-mode.md
QC: ../qc/2026-08-13-fix-cau-hoi-focus-mode.md — 3/3 PASS

## 1. Đã làm
Sửa `skills/tdq-conventions/SKILL.md` §1 bước 4 (Giao thức một turn), thêm 2 ý theo đúng
lựa chọn 1A/2A của user:
- **Bắt buộc** gọi `tdq_finish.py` để lint → append working log → set phase → graphify;
  **cấm** Edit/Read rồi tự append tay vào working log — kể cả khi bị `stop_gate.py` chặn
  (block nghĩa là "chưa gọi lệnh", không phải "gọi lệnh khác để né").
- Lệnh đó phải là **hành động cuối cùng** của turn, chạy TRƯỚC đoạn chat kết thúc turn
  (tóm tắt/câu hỏi/dòng `➤ Duyệt:`/báo lỗi vượt trần); sau khi in đoạn chat đó thì không
  gọi thêm tool nào nữa.

Không đụng các skill con (`tdq-intake`, `tdq-spec`, `tdq-plan`, `quick-lane`, `tdq-build`)
và không đụng `hooks/scripts/stop_gate.py`, đúng phạm vi đã chốt ở spec.

## 2. Bằng chứng sống (Q3 spec)
Đây là mục quan trọng nhất của request — không chỉ sửa văn bản mà còn phải chứng minh quy
tắc hoạt động NGAY trong chính các turn còn lại của request này. Working log
`docs/workinglog/2026-08-13.md` có các entry do `tdq_finish.py` tạo (không Edit tay):
- 18:27 — turn viết spec (kèm chuyển phase spec)
- 18:32 — turn viết plan
- entry của chính turn build/QC/report này (gọi ngay sau report này, không còn thao tác
  Edit tay nào lên working log kể từ lúc duyệt spec đầu tiên).

Điều này khác hẳn cả conversation trước đó (bao gồm request `focus-mode-an-cau-hoi`), nơi
100% entry working log được ghi bằng Edit tay, phản ứng lại sau khi bị `stop_gate.py` chặn
— đúng lỗ hổng thứ 2 đã phát hiện ở brief.

## 3. Test
- `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` → exit 0 (lần đầu FAIL R6
  do 121 dòng > trần 120, đã nén câu chữ ở bước 4 xuống còn 120 dòng).
- Không có unit test code — việc thuần sửa văn bản skill, đúng §4 spec.

## 4. Kết luận
DoD đạt: §1 bước 4 có đủ 2 ý bắt buộc, `doc_lint.py` xanh, và bằng chứng sống đã xuất hiện
liên tục xuyên suốt request. Rủi ro còn lại đúng như đã nêu ở spec §5: quy tắc mới chỉ có
hiệu lực nếu Claude thật sự tuân theo ở MỌI request sau này — không có cơ chế máy chặn nếu
quên (khác với `stop_gate.py`, vốn chặn được máy). Không có gợi ý xử lý thêm ngoài phạm vi.

Git: chưa commit.
