# MINI-SPEC/PLAN — Đánh giá cost/value từng thành phần tdq-workflow

Ngày: 2026-08-13 · Lane: quick · Brief: ../brief/2026-08-13-danh-gia-cost-value.md
Trạng thái: HOÀN THÀNH

## Phạm vi

- TRONG: 6 `SKILL.md` + 20 references, 3 agent, 6 hook script, `docs/claude-md-mau.md`,
  `scripts/` nằm trên đường chạy mỗi turn (`tdq_state`, `prompt_context`, `tdq_finish`).
- NGOÀI: `portable/` (bản đóng gói cố ý để share, cài project-level máy khác — không vào
  context Claude Code, không tính là trùng lặp) · sửa file sản phẩm · đo lại số cũ.
- Dùng lại số đo đã QC ở `reports/2026-08-13-ra-soat-toi-uu-llm.md`; không đo mới.
- Không web search: mọi ẩn số đều nội bộ, số liệu đã có trong repo.

## Task

- [x] **T1** (n5 e12m) Bảng cost/value cho từng CƠ CHẾ (không phải từng file): mỗi dòng
  đủ 6 cột `cơ chế · tốn gì (số thật) · đóng góp gì · nếu bỏ thì mất gì · đáng/không ·
  vì sao` — Test: `grep -c "^| "` mục đó ≥ 12 và không ô nào rỗng
- [x] **T2** (n3 e8m) Mục `## Nghẽn thật` chỉ giữ thứ vừa tốn vừa KHÔNG đóng góp cho
  chất lượng cuối; mỗi mục nêu rõ chất lượng cuối không giảm ở chỗ nào — Test: mỗi mục
  có ≥ 1 số đo và ≥ 1 câu về chất lượng cuối
- [x] **T3** (n3 e8m) Mục `## Đắt nhưng đáng` cho thành phần tốn nhiều mà là thứ giữ
  chất lượng — Test: có ≥ 3 thành phần, mỗi cái nêu hậu quả cụ thể nếu cắt
- [x] **T4** (n3 e10m) Viết `docs/tdq/reports/2026-08-13-danh-gia-cost-value.md`, bảng bề
  mặt loại hết dòng `portable/` — Test: `doc_lint` exit 0, `wc -l` ≤ 130, `grep -c portable`
  chỉ đếm được dòng giải thích phạm vi

## Definition of Done

1. `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-danh-gia-cost-value.md` exit 0.
2. `wc -l` báo cáo ≤ 130 dòng.
3. Bảng cost/value ≥ 12 dòng, đủ 6 cột, không ô rỗng.
4. `grep "portable/" ` báo cáo: không dòng dữ liệu nào, chỉ dòng nói về phạm vi.
5. `git status --short` không có file sản phẩm nào bị sửa.
6. `python3 -m pytest tests/ -q` exit 0.

## QC

| # | DoD | Lệnh | Kết quả | Phán quyết |
|---|---|---|---|---|
| 1 | Báo cáo sạch lint | `python3 scripts/doc_lint.py <report>` | exit 0 | PASS |
| 2 | Trần dòng | `wc -l <report>` | `99` (trần 130) | PASS |
| 3 | Bảng cost/value | `awk '/^## Bảng cost/,/^## Nghẽn/' <report> \| grep -c "^\| "` | `17` dòng (trần dưới 12), `grep -c "\| *\|"` = `0` ô rỗng | PASS |
| 4 | Không còn dòng dữ liệu portable | `grep -n portable <report>` | chỉ 1 dòng, là dòng nói về phạm vi (dòng 12) | PASS |
| 5 | Không sửa file sản phẩm | `git status --short` | chỉ tài liệu TDQ của request + file sổ sách do hook sinh | PASS |
| 6 | Suite xanh | `python3 -m pytest tests/ -q` | `535 passed, 206 subtests passed` | PASS |

DoD: 6/6 PASS, không vòng fix.
