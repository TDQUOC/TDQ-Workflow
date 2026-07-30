# QUESTIONS — external-agent-mode

## Vòng 1 (21:55) — 4 câu đổi kết quả

**C1. Kiến trúc engine của mode external?**
- (a) ĐỀ XUẤT: 2 runner riêng gọi CLI headless (`codex exec` / `agy -p`) qua Bash —
  một khuôn task + JSON report thống nhất, ép được report-file mỗi task, log riêng;
  plugin codex-plugin-cc vẫn cài để user dùng tay (/codex:review, /codex:rescue).
- (b) Codex đi qua plugin (/codex:rescue), chỉ agy dùng runner — ít code, nhưng 2 đường
  không đồng nhất, khó ép format report.
- (c) Qua MCP — cộng đồng báo chậm, loại trừ khuyến nghị.
- Đáp: **(a) — 2 runner riêng qua CLI**; plugin codex-plugin-cc vẫn cài để dùng tay.

**C2. Chính sách chọn model cho engine ngoài?**
- (a) ĐỀ XUẤT: mặc định theo engine + auto hạ/tăng theo cỡ task (codex: gpt-5.5,
  task nhỏ gpt-5.4-mini; agy: gemini-3.6-flash-medium, task khó gemini-3.1-pro-high);
  plan được phép override từng task. Danh sách codex khả dụng với ChatGPT auth sẽ
  verify thật lúc build.
- (b) Cố định 1 slug mỗi engine do user chốt.
- (c) Hỏi user chọn model mỗi lần duyệt plan.
- Đáp: **tuỳ chỉnh — hỏi model mỗi lần duyệt plan**, kèm luật: Claude fetch và trình
  list model AVAILABLE THẬT trên máy cho codex/agy; user trả 1–3 tên theo list:
  1 tên = default mọi task · 2 tên = [khó, dễ] · 3 tên = [khó, trung bình, dễ];
  Claude phân tích độ khó từng task và phân bổ đúng tier.

**C3. "Auto" chọn engine nghĩa là gì?**
- (a) ĐỀ XUẤT: theo loại task — code/refactor/test → codex; research/docs/UI → agy;
  hòa → codex.
- (b) Theo quota/tải còn lại.
- (c) Bỏ auto, luôn hỏi user.
- Đáp: **(a) — theo loại task** (code→codex, research/docs/UI→agy, hòa→codex).

**C4. Mức quyền ghi cho engine ngoài trong worktree?**
- (a) ĐỀ XUẤT: codex `--sandbox workspace-write` (cwd = worktree); agy không có sandbox
  FS → chạy `--dangerously-skip-permissions` nhưng cwd = worktree + task cấm path ngoài
  + Claude diff-check trước merge.
- (b) Chặt hơn: agy chỉ read-only xuất patch JSON, Claude apply hộ (chậm, 2 bước).
- (c) Cả hai full access — rủi ro cao, không khuyến nghị.
- Đáp: **(c) — CẢ HAI FULL ACCESS** (codex `danger-full-access`, agy
  `--dangerously-skip-permissions`). User chọn dù đã cảnh báo rủi ro; giảm thiểu còn
  lại: cwd = worktree + Claude diff-check trước merge (thuộc QC, không chặn engine).

## Vòng 2 (21:58) — 4 câu chốt nốt

- **C5. Tier plugin codex-plugin-cc?** → Đáp: **Luôn bật** (không đưa vào on_demand).
- **C6. Mode external áp lane nào?** → Đáp: **Cả quick lẫn full**.
- **C7. Granularity giao việc?** → Đáp: **(a) từng task đơn**, worktree chung cho phase.
- **C8. Engine hỏng task?** → Đáp: **(a) retry ≤2 lần kèm feedback lỗi, vẫn hỏng →
  Claude tự implement task đó**, ghi chú vào report. Không dừng giữa turn.

## Kết vòng interview

Không còn câu hỏi làm đổi kết quả — các chi tiết còn lại (cú pháp duyệt, vị trí file
report, cách probe model codex) là quyết định thiết kế, chốt trong spec.
