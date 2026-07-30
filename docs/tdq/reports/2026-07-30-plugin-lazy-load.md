# REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load

Ngày: 2026-07-30 · Spec: ../spec/2026-07-30-plugin-lazy-load.md (v1.0) · Plan/QC: cùng slug

## Vấn đề

49 plugin bật user-level → ~225 SKILL.md trên đĩa, catalog nhét vào mọi message
(~4–7k token), kèm xung đột hành vi (learning-output-style vs luật 1-turn, lumen spam
nhắc). Harness không có lazy-load thật (issue #42650) → cách duy nhất: tắt mặc định
+ bật khi cần.

## Đã làm gì

- **`scripts/plugin_tiers.py`** (+ bản copy `~/.claude/scripts/`, sha256 trùng):
  `status` / `reset` (ép false 6 always_off + 16 on_demand, atomic write + `.bak`,
  idempotent, không đụng key ngoài tier) / `enable <tên>` (chỉ nhận on_demand);
  lỗi input → ⚠️ + exit 0 không ghi đè; log ISO-timestamp
  `~/.claude/logs/plugin-tiers.log`, tắt bằng `PLUGIN_TIERS_LOG=0`. 15 test mới.
- **Cài user-level**: `~/.claude/plugin-tiers.json` (nguồn sự thật 6+16);
  `settings.json` 22 key false qua đúng một đường ghi (script); 2 hook
  `SessionEnd` + `SessionStart(startup)` chạy `reset` (tự tắt lại sau mỗi phiên,
  bù crash).
- **`~/.claude/CLAUDE.md`**: mục 11 "Năng lực & plugin (lazy-load)" 32 dòng — luật
  2 bước (ĐỀ XUẤT + HỎI user trước, đồng ý mới chạy lệnh enable + nhắc
  `/reload-plugins`), bảng định tuyến 16 dòng việc→plugin, đường đổi tier lâu dài;
  **viết lại §10** theo 0.3.3 (gộp T7.2 treo: tdq-intake/spec/plan/build, duyệt bằng
  chat thường, sạch tên lệnh cũ).

## Kết quả QC — PASS 9/9 vòng 1

`Ran 242 tests OK` (+15) · disabled đúng đủ 22 tên, không lẫn tier luôn-bật ·
round-trip enable→reset có log · 3 case an toàn (giữ nguyên ngoài-tier / settings
hỏng / tier hỏng → không ghi đè) pass cả unit lẫn chạy tay · CLAUDE.md grep sạch
tên cũ, audit claude-md-improver 3 góp ý (1 áp) · lint + `--pair` exit 0 ·
**skill trên đĩa 225 → 31** (yêu cầu ≤85) · hash 2 bản script trùng.

## Hợp đồng skill đã thi hành

update-config (T2.3–T2.4, schema settings/hooks) · hook-development (T2.4, cấu trúc
hook + giả lập `echo '{}' | … reset` exit 0) · claude-md-improver (T3.3, bảng góp ý
trong QC). `--pair` xác nhận đủ 3 khối 6 trường.

## Còn chờ user

1. Gõ `/reload-plugins` (hoặc restart) để catalog PHIÊN nhẹ theo — settings đã áp.
2. Quyết định commit (repo đang dồn 0.3.0→0.3.3 + request này, chưa commit gì).
