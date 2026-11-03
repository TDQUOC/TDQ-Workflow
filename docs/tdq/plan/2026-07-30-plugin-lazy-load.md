# PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)

Spec nguồn: `../spec/2026-07-30-plugin-lazy-load.md` (v1.0, duyệt 14:24) · Ngày: 2026-07-30

Mode thực thi: main — đa số task ghi vào `~/.claude/` (ngoài repo, worktree không cô
lập được) và đụng chung `settings.json` + `CLAUDE.md`, phụ thuộc tuần tự chặt.

## Năng lực → task

| Skill DÙNG (spec §3b) | Task |
|---|---|
| update-config | T2.3, T2.4 |
| hook-development (plugin-dev) | T2.4 |
| claude-md-improver (claude-md-management) | T3.3 |

## P1 — Script `plugin_tiers.py` + test (trong repo, red → green từng task)

- [x] **T1.1** Viết khung `scripts/plugin_tiers.py`: đọc `~/.claude/plugin-tiers.json`
  + `~/.claude/settings.json` (trong test, override gốc bằng biến môi trường `HOME`
  trỏ tmpdir); subcommand `status` in mỗi plugin 1 dòng `tên | tier | true/false`;
  sai cú pháp lệnh → exit 2.
  — Test: `tests/test_plugin_tiers.py::StatusTest` (HOME giả, 6+16 plugin, exit 0/2).
- [x] **T1.2** `reset`: ép `false` CẢ `always_off` LẪN `on_demand` trong
  `enabledPlugins`; atomic write (tmp + rename) + backup `.bak` một bản.
  — Test: `ResetTest::test_reset_sets_22_false` (settings giả 49 key → 22 false) +
  `test_backup_bak` (`.bak` tồn tại đúng 1 bản, nội dung = settings TRƯỚC khi ghi).
- [x] **T1.3** An toàn khóa ngoài tier: `reset`/`enable` không đổi bất kỳ key nào
  ngoài các key thuộc 2 danh sách (so sánh JSON phần còn lại trước/sau).
  — Test: `ResetTest::test_preserves_other_keys` (hooks/permissions/env giữ nguyên).
- [x] **T1.4** `enable <tên>`: chỉ nhận plugin thuộc `on_demand` → set `true`;
  tên lạ hoặc thuộc `always_off` → 1 dòng ⚠️ stderr, exit 0, không ghi file.
  — Test: `EnableTest` (3 case: on_demand ok, always_off từ chối, tên lạ từ chối).
- [x] **T1.5** Chịu lỗi input: `settings.json` hỏng/thiếu hoặc `plugin-tiers.json`
  hỏng/thiếu → 1 dòng ⚠️ stderr có timestamp, exit 0, KHÔNG ghi đè file nào.
  — Test: `BrokenInputTest` (4 case, so mtime/nội dung file không đổi).
- [x] **T1.6** Log service: mỗi lần reset/enable ghi `~/.claude/logs/plugin-tiers.log`
  dòng ISO-timestamp + plugin đổi giá trị cũ→mới; `PLUGIN_TIERS_LOG=0` → không ghi.
  — Test: `LogTest` (2 case).
- [x] **T1.7** Idempotent: `reset` lần 2 không đổi nội dung settings, log ghi
  "0 thay đổi". — Test: `ResetTest::test_idempotent`.

## P2 — Cài user-level

- [x] **T2.1** Tạo `~/.claude/plugin-tiers.json`: `always_off` = 6, `on_demand` = 16
  đúng danh sách spec §1. — Test: parse JSON, `len==6` và `len==16`, tên khớp spec.
- [x] **T2.2** Copy script sang `~/.claude/scripts/plugin_tiers.py`.
  — Test: `shasum -a 256` hai bản trùng nhau (DoD 8).
- [x] **T2.3** Sửa `~/.claude/settings.json`: chạy `plugin_tiers.py reset` lần đầu để
  22 key về `false` (đường ghi duy nhất, không sửa tay).
  — Test: `claude plugin list --disabled` chứa đúng đủ 22 tên §1, không lẫn tier luôn-bật.
  - Dùng: update-config
  - Nạp: gọi Skill `update-config` trước khi đụng `settings.json`
  - Để: nắm schema settings/enabledPlugins + hooks user-level để T2.3–T2.4 ghi đúng chỗ
  - Ra: `~/.claude/settings.json` bản mới (22 key false + 2 hook), backup `.bak`
  - Kiểm: lệnh test của T2.3 và T2.4 pass
  - Không dùng cho: sửa `~/.claude/CLAUDE.md` (P3 ghi trực tiếp theo spec)
- [x] **T2.4** Đăng ký 2 hook user-level trong `~/.claude/settings.json`:
  `SessionEnd` → `python3 ~/.claude/scripts/plugin_tiers.py reset`;
  `SessionStart` matcher `startup` → cùng lệnh.
  — Test: đọc lại settings đúng 2 entry; giả lập hook (`echo '{}' | python3 … reset`)
  exit 0.
  - Dùng: hook-development (plugin-dev)
  - Nạp: gọi Skill `plugin-dev:hook-development` trước khi viết cấu trúc hooks
  - Để: đặt đúng event/matcher/command tuyệt đối, hook không bao giờ chặn phiên (exit 0)
  - Ra: 2 entry hooks trong `~/.claude/settings.json`
  - Kiểm: lệnh test của T2.4 pass
  - Không dùng cho: hooks của plugin tdq-workflow (không đụng repo hooks/)
  (T2.4 áp dụng hợp đồng update-config đã khai tại T2.3 cho phần ghi settings.)
- [x] **T2.5** Round-trip thật: `enable postman` → key `true` → `reset` → về `false`
  (mô phỏng SessionEnd). — Test: đọc settings sau từng bước, log có 2 dòng tương ứng.
- [x] **T2.6** Chạy tay 3 case an toàn trên máy thật (DoD §6.4): settings thật trước/
  sau `reset` chỉ khác key tier; settings hỏng (bản sao tạm) → không ghi đè; tier hỏng
  (bản sao tạm) → không ghi đè. — Test: bằng chứng lệnh + output chép vào file QC.

## P3 — `~/.claude/CLAUDE.md`

- [x] **T3.1** Thêm mục "Năng lực & plugin (lazy-load)": luật 2 bước (đề xuất + HỎI
  user → user okay mới chạy `python3 ~/.claude/scripts/plugin_tiers.py enable <tên>`
  + in 1 dòng nhắc gõ `/reload-plugins`), bảng định tuyến đủ 16 dòng
  `| Việc chạm tới … | Bật plugin … |`, ghi chú review dùng built-in `/code-review`,
  mục ≤ 45 dòng. — Test: đếm dòng mục (từ heading tới heading kế) ≤ 45; đếm đúng
  16 dòng bảng; grep thấy bước "hỏi user" đứng TRƯỚC lệnh `plugin_tiers.py enable`;
  chạy nguyên văn lệnh enable trong mục với 1 plugin on-demand → exit 0.
- [x] **T3.2** Viết lại §10 theo 0.3.3: tdq-intake/spec/plan/build/status, duyệt bằng
  chat thường, giữ nguyên các gate còn hiệu lực (state chỉ qua `tdq_state.py`, lane
  quick/full, tick ngay, doc `docs/tdq/`). — Test: grep
  `tdq-start|tdq-analyze|tdq-approve` trong `~/.claude/CLAUDE.md` = 0 kết quả VÀ
  grep `tdq-intake`, `tdq-build` trong §10 ≥ 1 kết quả mỗi tên.
- [x] **T3.3** Audit toàn file CLAUDE.md sau sửa, áp góp ý hợp lý, ghi kết quả vào QC.
  — Test: mục QC có kết quả audit + cách xử lý từng góp ý.
  - Dùng: claude-md-improver (claude-md-management)
  - Nạp: gọi Skill `claude-md-management:claude-md-improver` sau khi T3.1–T3.2 xong
  - Để: soát chất lượng/mâu thuẫn của mục mới + §10 với phần còn lại của file
  - Ra: danh sách góp ý + diff đã áp, chép vào `docs/tdq/qc/<slug>.md`
  - Kiểm: lệnh test của T3.3 pass
  - Không dùng cho: tự viết lại các mục CLAUDE.md ngoài scope spec §1.4

## P4 — QC & đóng

- [x] **T4.1** Toàn suite + lint: `python3 -m unittest discover tests` OK (≥ 8 test
  mới); `doc_lint.py docs/tdq/spec` và `doc_lint.py --pair <spec> <plan>` exit 0.
  — Test: cả 3 lệnh exit 0.
- [x] **T4.2** Nghiệm thu catalog: nhờ user gõ `/reload-plugins`, chạy lại
  `scripts/skill_inventory.py`. — Test: ≤ 85 skill (DoD 7; cần 1 thao tác user).
- [x] **T4.3** Bổ sung (append, KHÔNG tạo mới đè) `docs/tdq/qc/<slug>.md` — file đã
  chứa bằng chứng T2.6 + audit T3.3 — thành bảng đủ 9 mục DoD spec §6 + report
  ≤ 50 dòng `docs/tdq/reports/<slug>.md` + working log. — Test: QC đủ 9 dòng
  PASS/FAIL kèm bằng chứng; `wc -l` report ≤ 50.

## Definition of Done

Theo đúng spec §6 (9 mục) — QC file T4.3 đối chiếu từng mục.
