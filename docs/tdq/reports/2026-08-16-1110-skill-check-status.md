# REPORT — Skill `tdq-check-status`

Ngày: 2026-08-16 · Lane: full · Mode: main · Plan: ../plan/2026-08-16-1110-skill-check-status.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

Thêm skill thứ 7 `tdq-check-status`: dò request TDQ đang dở bằng cách đọc thẳng ĐĨA, đối
chiếu với `state.json`, in báo cáo 6 mục và tiếp tục sau đúng một lần user gật. Nguyên tắc
gốc: **đĩa là bằng chứng, `state.json` là lời khai** — lệch nhau thì tin đĩa.

- `scripts/tdq_checkstatus.py` (mới): bộ dò CHỈ ĐỌC, lệnh `report`, cờ `--json --project
  --now`. Bảng cứng 11 ca lệch D1–D11, ba mức kết luận `TIẾP TỤC ĐƯỢC` / `VÁ RỒI TIẾP TỤC`
  / `CẦN USER QUYẾT`. Lệnh vá chỉ sinh từ hai họ `set` và `approve`, qua danh sách trắng.
- `skills/tdq-check-status/`: SKILL.md 7 bước + `references/report-template.md` +
  `references/bang-lech.md` (sinh từ hằng `CA_LECH`, test khoá cho khớp).
- `portable/workflow/05-check-status.md` + một dòng định tuyến trong `portable/AGENTS.md`.
- `skills/tdq-status/SKILL.md`: trỏ sang skill mới khi mất ngữ cảnh.
- `tests/test_check_status.py` (mới, 47 test) · `doc_lint.py` thêm trần dòng cho skill mới ·
  `CHANGELOG.md` + `plugin.json` lên 0.21.0.

## Kết quả kiểm

- Suite: `687 passed, 354 subtests passed in 38.30s` (nền trước request: 639).
- `doc_lint.py` mọi file đã sửa: exit 0.
- Chạy thật trên repo này: `report` exit 0, kết luận `TIẾP TỤC ĐƯỢC`, thời gian `0.06s`.
- Không ghi state: sha256 của `docs/tdq/state.json` không đổi trước/sau khi chạy `report`.

## Vòng fix QC

Agent `tdq-qc-tester` kiểm độc lập, tìm 5 lỗ hổng ngoài phạm vi test lúc đó — hai trong số
đó phá luật "không mất dữ liệu": state hỏng cú pháp bị coi như "chưa có request" (model yếu
sẽ chạy `init` và mất cả request), và `schema_version` kiểu chuỗi làm script exit 1. Đã vá
cả 5 (QC1.1–QC1.5) kèm test khoá. Chi tiết ở `../qc/2026-08-16-1110-skill-check-status.md`.

## Nợ kỹ thuật

- `code_rule_scan.py` báo `CHƯA KIỂM ĐƯỢC — thiếu ruff` cho cả 5 file Python: máy này chưa
  cài `ruff`. Đã bù bằng một lượt rà tay (bỏ hằng/helper/tham số thừa).
- D3 với **plan** chỉ ở mức `ok`: tick một task là plan đổi sha, giữ mức `chan` sẽ chặn oan
  mọi request đang implement. Đổi phạm vi plan vẫn phải nhìn bằng mắt.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| analyze | 18 phút | 6 phút | 1 |
| spec | 2 phút | 2 phút | 1 |
| plan | 4 phút | 4 phút | 1 |
| implement | 24 phút | 23 phút | 1 |
| qc | 17 phút | 17 phút | 1 |
| **Tổng** | **1 giờ 05 phút** | **52 phút** | |

## Commit

Chưa commit gì. Chờ user quyết.
