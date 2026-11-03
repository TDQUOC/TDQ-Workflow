# QC — Tối ưu plugin user-level: tier hoá + lazy-load

Ngày: 2026-07-30 · Plan: ../plan/2026-07-30-plugin-lazy-load.md · Vòng: 1

## Bằng chứng T2.6 — 3 case an toàn chạy tay trên máy thật

- **(a) settings thật chỉ khác key tier**: so sánh bản sao trước reset
  (`scratchpad/settings-before-reset.json`) với bản sau bằng python:
  `khóa ngoài enabledPlugins giữ nguyên: True` · `enabledPlugins ngoài tier giữ
  nguyên: True` · `.bak tồn tại: True` · superpowers (project khác) KHÔNG CÓ KEY,
  không bị đụng.
- **(b) settings.json hỏng** (HOME tạm, nội dung `{broken`): `reset` → 1 dòng
  `⚠️ không đọc được …settings.json: Expecting property name…`, exit 0, file vẫn
  nguyên `{broken` — không ghi đè.
- **(c) plugin-tiers.json hỏng** (HOME tạm, nội dung `[[[`): `reset` → 1 dòng
  `⚠️ không đọc được …plugin-tiers.json: Expecting value…`, exit 0, shasum
  settings trước/sau trùng — không ghi đè.

(Các mục DoD 1–9 sẽ bổ sung ở T4.3 — file này được append, không tạo mới đè.)

## Bằng chứng T3.3 — audit CLAUDE.md (skill claude-md-improver)

Rubric: mâu thuẫn nội bộ, tính hành-động-được, súc tích, đúng hiện trạng. Phạm vi:
mục 10–11 (không đụng mục 1–9 theo trường "Không dùng cho" của hợp đồng).

| Góp ý audit | Xử lý |
|---|---|
| §11 thiếu đường "đổi tier lâu dài" — model thấp không biết sửa đâu khi user muốn plugin luôn bật | ÁP: thêm 1 dòng trỏ về `plugin-tiers.json`, chỉ làm khi user yêu cầu rõ. Mục 11 = 32 dòng ≤ 45 |
| §10 mới bỏ dòng nhắc "➤ Để duyệt: gõ /tdq-workflow:tdq-approve…" của bản cũ | ĐÚNG CHỦ ĐÍCH: 0.3.3 đã xoá lệnh đó, hook tự in mã nhắc [TDQ:*] — không phải mất thông tin |
| §3 (Tavily) / §5 / §11: soát chéo — không mâu thuẫn; §11 định tuyến review về built-in khớp phán quyết nhóm 4 | Không cần sửa |

## Đối chiếu DoD spec §6 (vòng 1)

| # | Hạng mục | Bằng chứng | PASS/FAIL |
|---|---|---|---|
| 1 | Toàn suite + test mới | `Ran 242 tests … OK` (trước: 227 → +15 test mới, yêu cầu ≥8) | PASS |
| 2 | Chạy thật reset/enable | settings có đúng 22 key `false`; `claude plugin list` parse: disabled = 22 tên đúng danh sách (+`superpowers` vốn disabled sẵn vì scope project khác, script không đụng — không có key trong user settings); round-trip `enable postman` True → `reset` False | PASS |
| 3 | Log service | log thật 3 dòng ISO-timestamp (reset 22 thay đổi · enable postman False→True · reset 1 thay đổi); `LogTest` 2 case gồm `PLUGIN_TIERS_LOG=0` → không ghi | PASS |
| 4 | 3 case an toàn | unit: `test_preserves_other_keys`, `BrokenInputTest` (4 case); chạy tay: mục "Bằng chứng T2.6" ở trên | PASS |
| 5 | CLAUDE.md | grep `tdq-start\|tdq-analyze\|tdq-approve` = 0; `tdq-intake`/`tdq-build` ≥1; mục 11 = 32 dòng ≤45, đúng 16 dòng định tuyến, bước HỎI đứng trước lệnh enable; audit skill claude-md-improver: 3 góp ý, 1 áp (mục T3.3) | PASS |
| 6 | Lint | `doc_lint.py docs/tdq/spec` exit 0 · `--pair` spec/plan slug này exit 0 | PASS |
| 7 | Đo catalog | `skill_inventory.py` = **31 skill** trên đĩa (yêu cầu ≤85; trước: ~225). Catalog PHIÊN hiện tại chỉ nhẹ sau khi user gõ `/reload-plugins` | PASS |
| 8 | Đồng bộ 2 bản script | sha256 trùng `f8d1068d…` (repo ↔ `~/.claude/scripts/`) | PASS |
| 9 | Report + working log | report 50 dòng (wc -l, xem reports/ cùng slug); working log 2026-07-30 append đủ các mốc | PASS |

## Ghi chú lệch (có chủ ý)

1. T1.6/T1.7: log + idempotent nằm sẵn trong đường ghi từ T1.2/T1.4 → test viết sau,
   không có bước đỏ riêng (2 test vẫn kiểm hành vi thật, có case negative).
2. Bản CLI này không có `claude plugin list --disabled` (spec dẫn theo docs) →
   kiểm bằng `claude plugin list` + parse trạng thái, cùng giá trị đo.

## Kết luận

PASS 9/9 ở vòng 1 (không phát sinh task fix).
