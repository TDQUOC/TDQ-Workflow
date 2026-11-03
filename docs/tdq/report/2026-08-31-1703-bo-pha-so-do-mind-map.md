# REPORT — bỏ pha sơ đồ mind map khỏi quy trình TDQ

Ngày: 2026-09-01 · Plan: ../plan/2026-08-31-1703-bo-pha-so-do-mind-map.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

Pha `diagram` và cổng duyệt sơ đồ biến mất khỏi quy trình: spec duyệt xong là đi thẳng sang
plan, ở cả lane `full` lẫn lane nhanh. Xoá `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`
và skill `tdq-diagram`; `doc_lint.py` hết phụ thuộc vào chúng. 16 file trong `docs/tdq/mind-map/`
giữ nguyên làm tư liệu như user chốt.

Tương thích ngược: state cũ mang `phase=diagram` tự nâng về `spec` kèm cảnh báo, khoá `diagrams`
bị bỏ qua im lặng và biến mất khi ghi lại, ba lệnh cũ (`approve diagram`, `diagram add|list`)
thoát khác 0 kèm thông điệp nói rõ pha đã gỡ chứ không báo lỗi cú pháp chung chung.

## Phát hiện đáng chú ý

QC vòng 1 bắt được một lỗ thật: cổng vào pha `plan` trước nay chỉ được canh bằng danh sách sơ đồ,
nên gỡ pha sơ đồ đi là cổng rỗng — plan viết được trước khi user duyệt spec. Đã thêm
`_chan_spec_chua_duyet` để chặn đúng điều kiện `spec_approved = true` mà `phases.md` vẫn ghi,
kèm test khoá cả nhánh nghịch. QC vòng 2 PASS toàn bộ 17 mục DoD.

## Số liệu

- `pytest tests/ -q`: 101 failed, 1450 passed — bằng đúng mốc trước khi sửa, không file mới nào
  vào bảng lỗi.
- 3 bundle portable sinh lại ở 0.36.0, kiểm toàn vẹn CLEAN 90 / 138 / 83 file.
- `doc_lint` sạch trên `docs/tdq`, 4 skill đã dọn và `CHANGELOG.md`.

## Còn lại

- Nợ lint có sẵn ở `docs/archive/v0.1/` (25 vi phạm) và 2 vi phạm R5 trong `skills/` — byte y hệt
  HEAD, ngoài phạm vi request này.
- Thông điệp ba lệnh cũ viết bằng tiếng Anh; `_fail` in không kèm timestamp (nợ có sẵn).
- Chưa commit và chưa push — chờ user yêu cầu.
