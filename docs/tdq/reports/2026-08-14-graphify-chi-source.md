# REPORT — Tổ chức graphify: chỉ scan source, đọc có chủ đích

Ngày: 2026-08-14 · Lane: full · Mode: main · QC: 9/9 PASS
Spec: ../spec/2026-08-14-graphify-chi-source.md · Plan: ../plan/2026-08-14-graphify-chi-source.md

## Đã làm

- **Luật GHI**: `.graphifyignore` liệt kê đủ 8 thư mục (`tests/ docs/ portable/ skills/
  agents/ ClaudeExport/ claude-export/ graphify-out/`), kèm comment nhắc code mới phải nằm
  trong `scripts/` hoặc `hooks/`. Đồ thị chỉ còn mã sản phẩm kể cả khi chạy extract không cờ.
- **Đổi lối import 6 file hook** sang `from tdq_state import <tên>` — điều kiện CẦN để
  graphify nhìn thấy chuỗi `hooks → state`, vì graphify (cả 0.9.28 lẫn 0.9.42) không sinh
  cạnh cho dạng `import M` + `M.f()`.
- **Luật ĐỌC** vào `analyze-full.md` (bước 2) và `quick-lane.md`: mở đồ thị khi hỏi về
  liên kết / bản đồ tổng thể; grep khi tìm chuỗi hay đọc file cụ thể.
- **`graphify-out` vào `BOOKKEEPING_PATHS`** + test mới `test_digest_ignores_graphify_out`.

## Trước / sau

| Chỉ số | Trước | Sau |
|---|---|---|
| Node trong đồ thị | 1.421 (71% là test) | 412 |
| Cạnh `hooks/* → scripts/tdq_state.py` | 1 | 38 |
| `graphify affected "turn_snapshot()"` | không ra gì | ra `prompt_context.py:L75` |
| `git diff HEAD` mỗi prompt | ~5,1 MB | 0 byte phần `graphify-out` |
| Test suite | 535 passed | 536 passed |

## Việc còn treo

- `scripts/context_surface.py` và `scripts/skill_inventory.py` vẫn dùng `import tdq_state`
  (spec để NGOÀI phạm vi) — hai file này chưa hiện trong đồ thị dưới dạng cạnh gọi.
- Hai phép đo Q2 và Q7 đã chỉnh lại cách đo so với spec bản 1.0 đã duyệt (lý do + bằng
  chứng ở `docs/tdq/qc/2026-08-14-graphify-chi-source.md`). Điều kiện pass thực chất
  không đổi; nếu bạn không đồng ý với cách đo mới thì báo, tôi sửa lại.
- Không có commit nào được tạo trong lượt build này.
