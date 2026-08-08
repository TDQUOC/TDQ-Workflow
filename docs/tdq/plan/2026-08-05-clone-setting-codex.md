# PLAN — Skill clone-setting-to-codex

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-clone-setting-codex.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 1 bảng mapping nguồn sự thật duy nhất chi phối script lẫn skill.
Các task convert (P2) phụ thuộc chặt tuần tự lên nhau. Rủi ro bảo mật (secret thật
trong bundle) cần review liền mạch 1 luồng thay vì chia worktree song song. Khớp Lộ
trình đã chốt ở spec §1b ("Chia nhiều subagent song song | BỎ").
Trạng thái plan: CHỜ DUYỆT

## Năng lực → task
| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `skill-creator` | T1.1 | `skills/clone-setting-to-codex/SKILL.md` (frontmatter hợp lệ) |
| `tavily-*` | T1.2 | `skills/clone-setting-to-codex/references/mapping.md` có cột nguồn trỏ URL research |
| `mem0-memory` | T2.1 | Hàm đọc path trong `codex_clone.py` khớp fact đã lưu (`CODEX_HOME=~/.codex`...) |
| `graphify` | T5.4 | `graphify-out/graph.json`, `manifest.json` cập nhật, khớp code mới |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Scaffold skill
- [ ] **T1.1** Scaffold `skills/clone-setting-to-codex/SKILL.md` khung (frontmatter
  `name`/`description`, mục Cách dùng nêu rõ cảnh báo "ghi đè, không backup") — Test:
  `python3 scripts/skill_inventory.py` liệt kê `clone-setting-to-codex`
  - Dùng: `skill-creator`
  - Nạp: gọi skill `skill-creator` trước khi viết SKILL.md — theo đúng khuôn frontmatter
    chuẩn của skill-creator.
  - Để: scaffold đúng cấu trúc thư mục + frontmatter, tránh lỗi khuôn ngay từ đầu.
  - Ra: `skills/clone-setting-to-codex/SKILL.md` (frontmatter hợp lệ).
  - Kiểm: `python3 scripts/skill_inventory.py` liệt kê `clone-setting-to-codex`.
  - Không dùng cho: viết nội dung `references/mapping.md` (task T1.2 riêng).
- [ ] **T1.2** Viết `skills/clone-setting-to-codex/references/mapping.md` — bảng nguồn
  sự thật. Gồm 3 loại auto-convert: CLAUDE.md→AGENTS.md, skills→skills,
  mcpServers JSON→TOML. Cộng 5 loại không map: hooks, permissions, agents/*.md,
  commands/*.md, plugin. Mỗi loại kèm lý do kỹ thuật từ spec §3 — Test: file có đủ
  8 hàng mapping, mỗi hàng có cột "Nguồn" trỏ URL
  - Dùng: `tavily-*` (mcp)
  - Nạp: đã chạy ở phase analyze qua agent `search-scout`/`search-runner`
    (`docs/tdq/research/search/2026-08-05-clone-setting-codex/merged.json`, 12
    finding) — không gọi lại MCP trong plan này.
  - Để: đảm bảo mỗi dòng mapping có căn cứ nguồn chính thức, không suy đoán field.
  - Ra: `skills/clone-setting-to-codex/references/mapping.md` có cột nguồn trỏ URL.
  - Kiểm: đối chiếu tay — mỗi hàng mapping khớp ≥1 finding trong `merged.json`.
  - Không dùng cho: chạy thêm truy vấn tavily mới trong plan này.

**Xong P1 khi**: `SKILL.md` + `references/mapping.md` tồn tại, `skill_inventory.py`
liệt kê được skill mới.

## P2 — Script codex_clone.py: khung + convert 3 loại
- [ ] **T2.1** Khung `scripts/codex_clone.py`: argparse subcommand `apply`/`build`,
  hàm đọc `CLAUDE_HOME=~/.claude` và `CODEX_HOME` (mặc định `~/.codex`, override qua
  `--codex-home`), log service (timestamp ISO ra stderr, tắt qua `--quiet`) — Test:
  `python3 scripts/codex_clone.py --help` exit 0, liệt kê đủ 2 subcommand
  - Dùng: `mem0-memory` (mcp)
  - Nạp: đã `remember` fact cấu trúc Codex CLI ở phase analyze (id
    `20c67cf6-d5ee-45c4-9e9e-5dded24f07d7`) — không gọi lại MCP.
  - Để: đảm bảo path/field dùng đúng fact đã xác nhận (`CODEX_HOME=~/.codex`,
    `mcp_servers` snake_case...), không suy đoán lại từ đầu.
  - Ra: hàm đọc path trong `codex_clone.py` khớp fact đã lưu.
  - Kiểm: đối chiếu tay lúc review T5.2 — code khớp nội dung fact mem0 đã lưu.
  - Không dùng cho: lưu thêm fact mới trong plan này (chỉ dùng lại).
- [ ] **T2.2** Convert `~/.claude/CLAUDE.md` → `AGENTS.md` (copy nguyên văn) — Test:
  `test_agents_md_matches_source` — nội dung `AGENTS.md` sinh ra giống hệt
  `CLAUDE.md` nguồn
- [ ] **T2.3** Convert từng thư mục con `~/.claude/skills/<tên>/` → thư mục con
  `skills/<tên>/` phía đích (copy nguyên trạng cây thư mục) — Test:
  `test_skills_dirs_copied` — mọi skill trong nguồn có mặt trong đích, nội dung khớp
- [ ] **T2.4** Convert `mcpServers` (đọc từ `~/.claude.json`, field
  `command`/`args`/`env`) → khối `[mcp_servers.<tên>]` trong `config.toml` (TOML hợp
  lệ, tên khối snake_case) — Test: `test_mcp_servers_json_to_toml` — parse lại bằng
  `tomllib`, số server + field khớp nguồn
- [ ] **T2.5** Sinh `CODEX_CLONE_REPORT.md` liệt kê đủ 5 mục không map (hooks,
  permissions, agents/*.md, commands/*.md, plugin) kèm lý do (đọc từ
  `references/mapping.md`) — Test: `test_report_lists_unmapped_5_items`

**Xong P2 khi**: 4 test mới (T2.2–T2.5) PASS trên `tempfile` giả lập, không đụng
`~/.codex` thật.

## P3 — Subcommand apply + build
- [ ] **T3.1** `apply`: chạy 4 bước convert (T2.2–T2.5) ghi thẳng `$CODEX_HOME`. LUÔN
  ghi đè, không merge/backup. Log mỗi bước — Test: `test_apply_overwrites_no_backup`
  — chạy 2 lần liên tiếp trên `tempfile`, lần 2 đè sạch nội dung cũ, không sinh file
  `.bak-*`
- [ ] **T3.2** `build --dest <path> [--zip]`: sinh bundle vào thư mục chỉ định (không
  đụng `~/.codex` thật), in banner cảnh báo "bundle chứa secret thật" ra stdout mỗi
  lần chạy; `apply` KHÔNG in banner này — Test: `test_build_prints_secret_banner_apply_does_not`
- [ ] **T3.3** Chặn cứng 4 field lỗi thời không bao giờ được ghi ra
  (`ask_for_approval`, `sandbox`, `experimental_use_rmcp_client`, top-level `[env]`)
  — Test: `test_deprecated_fields_never_written` — grep `config.toml` sinh ra không
  chứa 4 chuỗi này

**Xong P3 khi**: T3.1–T3.3 PASS, `apply` và `build` đều chạy được trên `tempfile`.

## P4 — Log & test bắt buộc
- [ ] **T4.1** Rà soát log service: mọi bước convert (T2.2–T2.5) và cả `apply`/`build`
  đều có dòng `log()` timestamp ISO; `--quiet` tắt được toàn bộ — Test: chạy `apply`
  không `--quiet` trên `tempfile` → có ≥5 dòng log; chạy lại kèm `--quiet` → stdout/stderr
  rỗng ngoài lỗi
- [ ] **T4.2** Chạy toàn bộ `tests/test_codex_clone.py` bằng một lệnh — Test:
  `cd tests && python3 -m unittest test_codex_clone -v` → toàn bộ PASS, 0 lỗi/fail

**Xong P4 khi**: T4.2 xanh hoàn toàn.

## P5 — Chạy thật + review + QC
- [ ] **T5.1** Chạy `apply` thật trên máy user: `python3 scripts/codex_clone.py apply`
  — Test: exit 0; `~/.codex/AGENTS.md` giống hệt `~/.claude/CLAUDE.md`;
  `~/.codex/config.toml` parse được bằng `tomllib`; `~/.codex/skills/*` đủ số skill
  nguồn
- [ ] **T5.2** Review sâu bằng agent `tdq-reviewer` (đọc `codex_clone.py` + spec, tìm
  lỗ hổng thiết kế/mâu thuẫn) — Test: agent trả kết quả; mọi defect nghiêm trọng được
  fix ngay (thêm task con nếu cần), loop đến khi không còn defect chưa nêu ở spec §5
- [ ] **T5.3** QC độc lập bằng agent `tdq-qc-tester`: chạy `apply` trên
  `$CODEX_HOME` giả lập (temp dir qua `--codex-home`). Xác nhận phạm vi ghi CHỈ đúng
  các file khai báo ở spec §2, không đụng file khác trong thư mục giả lập. Đối chiếu
  đủ Q1–Q8 của spec §6 — Test: agent trả PASS kèm bằng chứng từng mục Q1–Q8
- [ ] **T5.4** Cập nhật code graph — Test: `graphify extract . --code-only` exit 0,
  `graphify-out/graph.json` có timestamp mới
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` trước khi chạy lệnh — dùng đúng cú pháp
    `extract . --code-only` đã quy ước trong CLAUDE.md §7.
  - Để: đồng bộ code graph với `codex_clone.py` + skill mới vừa thêm.
  - Ra: `graphify-out/graph.json`, `graphify-out/manifest.json`,
    `graphify-out/GRAPH_REPORT.md` cập nhật.
  - Kiểm: `git diff --stat graphify-out/` cho thấy file đổi; lệnh extract thoát mã 0.
  - Không dùng cho: không phân tích kiến trúc sâu hơn phạm vi file đã sửa.
- [ ] **T5.5** Viết `docs/tdq/reports/2026-08-05-clone-setting-codex.md` + ghi
  `docs/workinglog/2026-08-05.md` — Test: `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-05-clone-setting-codex.md` exit 0; `tail -5 docs/workinglog/2026-08-05.md` có dòng mới đúng ngày hôm nay

**Xong P5 khi**: T5.1–T5.4 PASS, T5.5 đã ghi.

## QC bổ sung (nếu T5.3 FAIL)
(Thêm task fix trực tiếp vào đây khi QC phát hiện lỗi, không cần duyệt lại plan.)

## Definition of Done
Trỏ về spec §6 (8 hạng mục Q1–Q8):
- Q1 = T4.2 (test suite PASS)
- Q2 = T5.1 (apply chạy thật, exit 0, file tồn tại không rỗng)
- Q3 = T5.1 (AGENTS.md khớp nguồn)
- Q4 = T2.4 + T5.1 (MCP servers TOML hợp lệ, đủ số server)
- Q5 = T2.5 (report đủ 5 mục không map)
- Q6 = T3.2 (banner cảnh báo secret khi build, không có khi apply)
- Q7 = T5.2 (review độc lập tdq-reviewer)
- Q8 = T5.3 (QC hành vi ghi đè đúng phạm vi, tdq-qc-tester)
Cộng: skill `clone-setting-to-codex` lên `skill_inventory.py` (T1.1);
`doc_lint.py` exit 0 trên `SKILL.md`/`references/mapping.md`; `graphify extract`
đã chạy (T5.4); working log đã ghi (T5.5).
