# QUICK — Format câu hỏi interview: mỗi option 1 dòng

Ngày: 2026-08-05 · Request: ../requests/2026-08-05-format-cau-hoi-interview.md · Lane: quick
Trạng thái: ĐÃ DUYỆT (10:38, nguyên văn "duyệt quick", kèm 3 phương án đề xuất 1A/2A/3A)
Năng lực: không có (chỉ sửa tài liệu skill/portable + 1 nhóm test)

## Phạm vi

- Trong: khuôn trình bày câu hỏi có option ở bộ workflow TDQ — vòng interview, chốt lane,
  chốt mode, câu mở cuối vòng. Bỏ ưu tiên `AskUserQuestion`.
- NGOÀI: nội dung câu hỏi hỏi cái gì · luật lane/gate/duyệt · file tài liệu của các
  request cũ (giữ nguyên câu chữ lịch sử).

## Task

- [x] **T1** Viết lại mục "Hỏi thế nào" của `skills/tdq-intake/references/interview.md`:
  khuôn `- A (đề xuất): nội dung`, 6 luật khuôn, câu mở cuối vòng cùng dạng —
  Test: `test_skill_docs.OptionMotDongTest.test_khuon_mau_co_option_moi_dong`
- [x] **T2** Đồng bộ chốt lane ở `skills/tdq-intake/SKILL.md` bước A2 và
  `portable/workflow/01-intake.md` bước 2 + bước 4 —
  Test: `test_chot_lane_cung_dung_khuon`, `test_cam_gop_option_vao_doan_van`
- [x] **T3** Bỏ ưu tiên `AskUserQuestion`, thay bằng "luôn hỏi bằng danh sách trong chat" —
  Test: `test_khong_con_uu_tien_askuserquestion`, `test_luat_hoi_bang_danh_sach_trong_chat`
- [x] **T4** Trỏ khuôn cho câu hỏi chốt mode ở `skills/tdq-conventions/references/approval.md`,
  `skills/tdq-plan/SKILL.md`, `portable/workflow/03-plan.md` — Test: `doc_lint.py skills portable`
- [x] **T5** Ghi luật vào bản lõi `portable/claude-md/CLAUDE.md` rồi cài sang `~/.claude` —
  Test: `test_claude_md_core` (5 ca, trần 3.500 byte)

## Definition of Done

- `cd tests && python3 -m unittest discover -s . -p "test_*.py"` → 575 test, 0 fail.
- `python3 scripts/doc_lint.py skills portable` → exit 0.
- Không còn chuỗi `AskUserQuestion nếu có` trong `skills/` và `portable/`.
