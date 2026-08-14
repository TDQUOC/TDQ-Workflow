# REPORT — Đề xuất cơ chế chống quick-fix phá kiến trúc

Ngày: 2026-08-14 · Lane: full · Mode: main (inline) · Spec 1.0 · 13/13 task `[x]`

## Đã làm

- Đo lại 4 khoảng trống bằng lệnh thật: chữ "kiến trúc" xuất hiện **1** lần trên 1.844
  dòng skill (ở bảng chọn lane); luật code chỉ có 1 dòng `tdq-build/SKILL.md:51`;
  `god-nodes` xuất hiện **0** lần, `affected` 2 lần và cả 2 chỉ là gợi ý đọc; luật
  `qc.md:7` đóng cứng "số hạng mục QC = số dòng DoD".
- Viết `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` — 6 mục, 6 cơ chế M1–M6, mỗi
  cơ chế đủ 5 trường (chặn triệu chứng nào · chèn vào file:mục nào · mức A/B · nguyên văn
  dòng luật copy dán được · một lệnh kiểm). M1 hồ sơ kiến trúc · M2 ô ràng buộc trong
  spec §5 · M3 luật "tìm rồi mới tạo" thay dòng implement cũ · M4 khai `Chạm:` trong plan
  · M5 ba hạng mục QC cố định (nới luật cũ, nêu rõ dòng bị nới) · M6 cổng trùng lặp jscpd.
- Ba gói cộng dồn: tối thiểu (M2+M3, thuần văn bản) · vừa (M1–M5, vẫn không script) ·
  đầy đủ (thêm M6). **Khuyến nghị gói vừa.**
- Bản express rút gọn cho từng cơ chế, và mục "áp cho project khác" tách rõ phần độc lập
  ngôn ngữ với phần phải tự chỉnh (Unity, game). Loại thẳng fitness function theo stack.
- Kiểm chứng bằng chạy thật, không suy đoán: `graphify god-nodes` và
  `graphify affected "payload_cwd"` cho ví dụ trong M1/M4; `jscpd` 5.0.15 xác nhận đủ 3
  cờ dùng trong M6, quét repo này ra 72 cặp trùng / 1.82% token, exit 0.

## QC

11/11 PASS vòng 1 — chi tiết ở `docs/tdq/qc/2026-08-14-chong-no-ky-thuat.md`.
`pytest tests/ -q` → 563 passed, 244 subtests. `doc_lint` (3 file và `--pair`) → exit 0.
`git status --porcelain -- skills scripts hooks` rỗng: đúng phạm vi, không đụng workflow.
Log service: BỎ — request chỉ tạo tài liệu Markdown, không có runtime.

## Còn lại

Chưa commit — chờ user quyết. Việc thực thi cơ chế vào `skills/` là request riêng, đúng
như user chốt ở vòng scope (5B).
