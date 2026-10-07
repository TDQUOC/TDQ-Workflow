# PLAN — Gỡ Lumen và tối ưu luật tìm kiếm 3 tầng

Ngày: 2026-10-07 · Spec: ../spec/2026-10-07-2041-go-lumen-toi-uu-tim-kiem.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user chọn "1b" (inline); đề xuất ban đầu subagent theo `tdq_bench simulate` (chênh 18,3 phút)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thang kiểm không lumen
- P2 — Gate dẫn tới tầng sống
- P3 — Hook TDQ chạy trong Codex
- P4 — Luật chữ 3 tầng
- P5 — Phát hành 0.58.0
- P6 — Đo trước/sau
- P7 — Dọn máy user (cuối cùng)
- Px — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P7 chỉ chạy khi P1–P6 xong và `tron-bo` xanh.
2. Mỗi task: `[~]` khi bắt đầu → test đỏ trước → sửa → test xanh → `[x]` NGAY.
3. Mỗi bước: `python3 scripts/tdq_test.py vung-cham`; trọn bộ chỉ ở cuối P5 và ở QC.
4. Lệnh chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` trên chính lệnh đó.
5. Phiên thử (P6) chạy trên bản sao `git clone --local` ở `%TEMP%`; Claude Code nạp plugin TDQ từ cây làm việc bằng `--plugin-dir <repo>` và tắt `tdq-workflow@tdq-local` (bản cache 0.57.0) trong `--settings`, để hook chạy đúng mã mới.
6. Sửa file ngoài repo (P7): bản sao `<file>.truoc-tdq-<YYYYMMDDHHMMSS>.bak` trước khi ghi.
7. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass. Không commit/push cho đến khi user yêu cầu.

## P1 — Thang kiểm không lumen
- [x] **T1.1** (e25m) `tdq_lsp.py`: xoá `bac5_lumen`, `_model_lumen`, `_model_da_pull`, `_index_cu_hon_code`, `_lumen_tra_loi_duoc`, `_binary_lumen`, `_lumen_thieu_binary_windows`, `_ollama_dang_chay`, lệnh `wake`/`nha` và hằng số lumen/ollama; đánh số lại bậc 6→5, 7→6, 8→7; `kiem_mot_lenh` tổng hợp smoke 3 tầng; docstring đầu file theo 7 bậc — Test: `python3 -m pytest tests/test_tdq_lsp.py tests/test_mot_lenh_kiem.py -q` xanh; `test_bac_lumen_hieu_ung.py` xoá
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`, `tests/test_mot_lenh_kiem.py`, `tests/test_bac_lumen_hieu_ung.py` → `main()` (hub), `chay_kiem`, `kiem_mot_lenh`; người import: `tdq_setup`, `tdq_finish`, `tdq_codex_mcp`, `setup_status`
- [x] **T1.2** (e20m) `tdq_setup.py`: xoá `kiem_cau_hinh_lumen`, tầng lumen trong `smoke_bon_tang` (đổi thành smoke 3 tầng), phần dựng nền `lumen()` và `TIMEOUT_LUMEN_NEN`, `TANG_SAN_SANG` còn grep/lsp/graphify; khối hướng dẫn ghim (`khoi_huong_dan`) viết theo luật 3 tầng — Test: `python3 -m pytest tests/test_tdq_setup.py tests/test_tu_khoi_tao.py -q` xanh
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`, `tests/test_tu_khoi_tao.py` → `main()` (hub), `khoi_tao_nen`, `ghim_huong_dan_tool`
  - Cần: T1.1
- [x] **T1.3** (e8m) `tdq_finish.py`: xoá bước `reindex` (`step_reindex`, `REINDEX_TIMEOUT`, chỗ gọi, dòng tóm tắt); xoá `tests/test_finish_reindex.py` — Test: `python3 -m pytest tests/test_tdq_finish.py -q` xanh, `tdq_finish.py` không in `reindex`
  - Chạm: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py`, `tests/test_finish_reindex.py` → `main()` của `tdq_finish`
  - Cần: T1.1
- [x] **T1.4** (e12m) `setup_status.py` + `setup_status_render.py`: bỏ phụ thuộc `lumen`/`ollama` khỏi bảng, `thu_lumen`, `_endpoint_lumen`, khối "lumen — model embedding" — Test: `python3 -m pytest tests/test_setup_status.py tests/test_setup_status_render.py -q` xanh
  - Chạm: `scripts/setup_status.py`, `scripts/setup_status_render.py`, `tests/test_setup_status.py`, `tests/test_setup_status_render.py` → `thu_tat_ca`, `render`
  - Cần: T1.1
- [x] **T1.5** (e6m) `session_start.py`: `TANG` còn grep/lsp/graphify; câu nhắc dựng nền bỏ "lumen index" — Test: `python3 -m pytest tests/test_tu_khoi_tao.py -q` xanh, thêm ca: dấu mốc đủ 3 tầng sẵn sàng → `can_khoi_tao` False
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_tu_khoi_tao.py` → `can_khoi_tao`
  - Cần: T1.2

**Xong P1 khi**: `vung-cham` xanh; `grep -i lumen scripts/tdq_lsp.py scripts/tdq_setup.py scripts/tdq_finish.py scripts/setup_status*.py hooks/scripts/session_start.py` chỉ còn chú thích lịch sử.

## P2 — Gate dẫn tới tầng sống
- [x] **T2.1** (e15m) `search_rules.py`: thay hằng `LOI_RA` bằng hàm `loi_nhac(tang_song)` — mỗi tầng sống một dòng lệnh dùng ngay (LSP: `mcp__lsp__start_lsp` rồi `find_symbol`/`find_references`; graphify: `graphify query "<câu hỏi>"`), không tầng nào → câu đứng xuống; bỏ regex `LUMEN` và nhánh lumen của `la_goi_khai_niem`; `start_lsp` vẫn KHÔNG tính (lời gọi dọn dẹp, giữ allowlist) — lời gọi LSP lỗi đã được ghi ở PreToolUse (T2.3) — Test: `python3 -m pytest tests/test_search_rules.py -q` xanh, ca mới: lời nhắc không chứa "lumen", chỉ liệt kê tầng sống
  - Chạm: `scripts/search_rules.py`, `tests/test_search_rules.py`, `tests/test_search_replay.py` → `quyet_dinh`, `la_goi_khai_niem`; người dùng: `search_gate`, `search_observe`, `search_replay`
- [x] **T2.2** (e12m) `search_gate.py`: `TANG_KHAI_NIEM` = (lsp, graphify); đọc dấu mốc một lần, truyền tầng sống vào lời nhắc; log dòng "nhắc tầng: …" — Test: `python3 -m pytest tests/test_search_gate.py -q` xanh, ca mới: dấu mốc chỉ graphify sống → lời chặn chỉ nhắc graphify
  - Chạm: `hooks/scripts/search_gate.py`, `tests/test_search_gate.py` → `quyet`, `ly_do_dung_xuong`
  - Cần: T2.1
- [x] **T2.3** (e10m) Ghi sổ lời gọi LSP ở PreToolUse: `hooks/hooks.json` thêm PreToolUse matcher `mcp__lsp__.*` → `search_observe.py`; PostToolUse bỏ tên tool lumen; `search_observe.py` ghi `khai_niem` khi nhận PreToolUse của LSP (chống ghi đôi khi Post cũng đến) — Test: `python3 -m pytest tests/test_search_observe.py -q` xanh, ca mới: chỉ có PreToolUse của `find_symbol` (Post không tới vì lỗi) → grep kế tiếp được cho qua
  - Chạm: `hooks/hooks.json`, `hooks/scripts/search_observe.py`, `tests/test_search_observe.py` → `ghi_so`, `trang_thai`
  - Cần: T2.1

## P3 — Hook TDQ chạy trong Codex
- [x] **T3.1** (e20m) Trinh sát: 1 câu tra web về cách codex-cli 0.155 nạp `.codex/hooks.json` của dự án; rồi trên bản sao tạm đặt `tests/probe_codex_hook.py` làm hook PreToolUse duy nhất, chạy `codex exec -s workspace-write` một câu ngắn; phân biệt (a) hook không được gọi, (b) được gọi nhưng `python3` hỏng/bị chặn, (c) chạy được nhưng ghi sổ sai thư mục. Ghi `docs/tdq/research/2026-10-07-2041-hook-codex.md` — Test: file research có lệnh, output thật, và nguyên nhân thuộc đúng một trong (a)(b)(c) hoặc "khác" kèm bằng chứng
- [x] **T3.2** (e20m) Sửa theo nguyên nhân T3.1 (đường lệnh hook, cách gọi python, hoặc cấu hình cần bật); `.codex/hooks.json` thành bản chính thức (edit gate + search gate + observe), xoá `.codex/hooks.json.truoc-tdq-20261007144243.bak`; `tdq_codex_mcp.py` chỉ khai MCP `lsp`, bỏ `_tim_lumen`/`_nguon_lumen`; 2 test hooks json và test edit gate đòi đúng bộ matcher mới — Test: `python3 -m pytest tests/test_codex_hooks_json.py tests/test_codex_edit_gate.py tests/test_codex_mcp.py tests/test_codex_search_gate.py -q` xanh
  - Chạm: `.codex/hooks.json`, `scripts/tdq_codex_mcp.py`, `scripts/tdq_codex.py`, `tests/test_codex_hooks_json.py`, `tests/test_codex_edit_gate.py`, `tests/test_codex_mcp.py`, `tests/test_codex_search_gate.py` → `khai_mcp_codex`, `kiem_hook_ban`
  - Cần: T3.1, T2.3

## P4 — Luật chữ 3 tầng
- [x] **T4.1** (e20m) Viết lại `skills/tdq-setup/references/uu-tien-tim-kiem.md` + `uu-tien-tim-kiem-chi-tiet.md`: 3 tầng, bảng loại câu hỏi (khái niệm mơ hồ → `graphify query` song song grep đồng nghĩa, kèm số đo 11–12/12 của request 1843), mục phụ thuộc runtime không còn ollama, mục gate theo lời nhắc mới; câu chuẩn trích ở mọi điểm móc — Test: `python3 -m pytest tests/test_luat_4_tang.py tests/test_tdq_setup_skill.py tests/test_claude_md_core.py -q` xanh (sửa ca ghim chữ "lumen" thành 3 tầng)
  - Dùng: tdq-setup
  - Để: nguồn luật 4 tầng gốc + `ghim_huong_dan_tool`, nạp skill TRƯỚC bước đỏ
  - Ra: `skills/tdq-setup/references/uu-tien-tim-kiem.md` bản 3 tầng
  - Kiểm: `grep -ci lumen skills/tdq-setup/references/uu-tien-tim-kiem*.md` chỉ còn câu lịch sử "đã gỡ 0.58.0"
  - Không dùng cho: chạy `tdq_setup.py main` (cài/vá máy)
  - Chạm: `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md`, `tests/test_luat_4_tang.py`, `tests/test_tdq_setup_skill.py`, `tests/test_claude_md_core.py`
- [x] **T4.2** (e20m) Sửa 4 câu chấm oan: `analyze-full.md:33-39`, `quick-lane.md:42`, `tdq-build/SKILL.md:66`, `PHASE_TABLE` (`tdq_state.py:1194,1209`) thành "LSP + một tầng khái niệm đang sống (graphify), grep sau"; sinh lại `skills/tdq-conventions/references/phases.md` bằng `tdq_state.py phases-doc` — Test: `python3 -m pytest tests/test_luat_skill.py tests/test_luat_gon.py -q` xanh; `grep -rn "lumen" skills/tdq-intake skills/tdq-build scripts/tdq_state.py` rỗng
  - Chạm: `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-build/SKILL.md`, `scripts/tdq_state.py`, `skills/tdq-conventions/references/phases.md` → `PHASE_TABLE`
  - Cần: T4.1
- [x] **T4.3** (e12m) `skills/tdq-setup/SKILL.md` (7 bậc, bỏ mục lumen/Ollama), xoá `skills/tdq-setup/references/lumen.md`, `reminder-codes.md` (`TDQ:SEARCH` 2 tầng khái niệm), `plugin-routing.md` bỏ dòng lumen, `skill_tokens.py` bỏ "lumen" khỏi danh sách plugin; soát `grep -rn "bậc [5-8]"` trên `scripts/ hooks/ skills/ tests/` khớp thang 7 bậc — Test: `doc_lint.py` các file skill sửa exit 0; lệnh grep không còn số bậc lệch
  - Chạm: `skills/tdq-setup/SKILL.md`, `skills/tdq-setup/references/lumen.md`, `skills/tdq-conventions/references/reminder-codes.md`, `skills/tdq-conventions/references/plugin-routing.md`, `scripts/skill_tokens.py`
  - Cần: T1.1, T4.1

## P5 — Phát hành 0.58.0
- [x] **T5.1** (e10m) Xoá `.lumenignore` + `tests/test_lumenignore.py`; `.gitignore` bỏ dòng `.tdq-lumen-index`; xoá file mốc `docs/tdq/.tdq-lumen-index` nếu có; `CHANGELOG.md` mục 0.58.0; `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` → `0.58.0` — Test: `python3 -m pytest tests/test_plugin_tiers.py -q` xanh + kiểm đồng bộ version (`grep '"version"'` 2 file = 0.58.0); rồi `python3 scripts/tdq_test.py tron-bo` 0 module đỏ
  - Chạm: `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.lumenignore`, `.gitignore`, `tests/test_lumenignore.py` → `Changelog` (hub)
  - Cần: T1.5, T2.3, T3.2, T4.3

## P6 — Đo trước/sau
- [x] **T6.1** (e15m) Q3: `tdq_lsp.py check` trên máy (lumen vẫn cài lúc này — thang không còn hỏi tới) → ghi `docs/tdq/bench/2026-10-07-2041-sau-khi-go/thang-kiem.md` — Test: 7 bậc đánh số liền, smoke 3 tầng, dòng tổng ĐẠT, exit 0
  - Cần: T5.1
- [x] **T6.2** (e20m) Q4: phiên thử Claude Code 2 lần, đúng câu hỏi của request 1843, bản sao repo mới, `--plugin-dir <repo>` + `--settings` tắt `lumen@…` và `tdq-workflow@tdq-local` → `claude-code.md` (đếm lượt thừa: lượt bị chặn + lượt gọi tool không tồn tại + lượt LSP lỗi trước khi grep chạy được) — Test: lần xấu hơn ≤ 1 lượt thừa; lời chặn không chứa "lumen"
  - Cần: T5.1
- [x] **T6.3** (e15m) Q5: phiên `codex exec -s workspace-write` trên bản sao → `codex.md`, kèm trích sổ `docs/tdq/.tdq-search.jsonl` của bản sao — Test: ≥ 1 dòng sổ mang khoá phiên Codex
  - Cần: T5.1

## P7 — Dọn máy user (cuối cùng)
- [x] **T7.1** (e10m) Sao lưu rồi sửa: `~/.claude/settings.json` (bỏ `lumen@claude-plugins-official` khỏi `enabledPlugins`, bỏ env `OLLAMA_HOST`, `LUMEN_EMBED_MODEL`); `claude plugin uninstall lumen@claude-plugins-official`; `~/.codex/config.toml` bỏ khối `[mcp_servers.lumen]` → ghi `docs/tdq/bench/2026-10-07-2041-sau-khi-go/may-user.md` — Test: `grep -i lumen ~/.claude/settings.json ~/.codex/config.toml` rỗng; 2 file `.bak` tồn tại; `codex mcp list` không có lumen
  - Cần: T6.1, T6.2, T6.3
- [x] **T7.2** (e5m) Xoá `~/.local/share/lumen`, `~/.config/lumen`, thư mục cache plugin lumen nếu `uninstall` còn sót; `ollama rm qwen3-embedding:0.6b` — Test: 3 thư mục không còn; `ollama list` không có `qwen3-embedding:0.6b`
  - Cần: T7.1
- [x] **T7.3** (e5m) Cập nhật khối luật trong `~/.claude/CLAUDE.md` bằng cách gọi đúng `tdq_setup.ghim_huong_dan_tool` (không chạy `main`), có bản sao trước — Test: khối giữa 2 dấu mốc là bản 3 tầng, phần user tự viết quanh nó y nguyên (so diff ngoài khối = rỗng)
  - Cần: T4.1

## Px — Log & test bắt buộc
- [x] **Tx.1** (e3m) Log: dòng log mới "nhắc tầng: …" của `search_gate` và dòng ghi sổ PreToolUse của `search_observe` theo `TDQ_LOG` sẵn có — Test: chạy hook với payload mẫu, stderr có dòng log có timestamp; `TDQ_LOG=0` thì im
  - Cần: T2.2, T2.3
- [x] **Tx.2** (e8m) Trọn suite một lệnh — Test: `python3 scripts/tdq_test.py tron-bo` 0 module đỏ
  - Cần: T5.1, Tx.1

## Cụm song song
Ba cụm mã độc lập, gộp ở P5: cụm A = P1 (thang kiểm); cụm B = P2 (gate) → T3.2; cụm C = T3.1 (trinh sát Codex, không sửa repo) và P4 sau T1.1. File nóng: `tests/test_tu_khoi_tao.py` (T1.2, T1.5) — một chủ ghi: T1.2 làm trước, T1.5 nối tiếp trong cùng cụm A. P6, P7 tuần tự sau P5.

## QC vòng 1 — fix
- [x] **QC1.1** `skills/tdq-build/references/rules/chung.md:81` còn "one round of lumen or grep" → `graphify query` — Test: `doc_lint` 0 vi phạm, `token_budget.py` ghi lại khoá, 261 ca test chạm luật xanh

## Definition of Done
Trỏ về §6 của spec, mỗi dòng một lệnh kiểm:

- [x] Q1 mã không còn lumen — `grep -rn -i lumen scripts hooks` chỉ còn dòng chú thích lịch sử (liệt kê từng dòng + lý do vào qc)
- [x] Q2 luật 3 tầng — `grep -rn -i lumen skills scripts/tdq_state.py` chỉ còn câu lịch sử; bảng trong `uu-tien-tim-kiem.md` có đúng 3 tầng
- [x] Q3 thang 7 bậc — `python3 scripts/tdq_lsp.py check; echo $?` → 7 bậc, smoke 3 tầng, ĐẠT, 0
- [x] Q4 gate ≤ 1 lượt thừa — đếm trong `docs/tdq/bench/2026-10-07-2041-sau-khi-go/claude-code.md` (2 lần chạy)
- [x] Q5 hook Codex chạy — `grep -c <khoá phiên codex> <bản sao>/docs/tdq/.tdq-search.jsonl` ≥ 1
- [x] Q6 test — `python3 scripts/tdq_test.py tron-bo` 0 module đỏ
- [x] Q7 hồi quy hub — `python3 -m pytest tests/test_tdq_lsp.py tests/test_tdq_setup.py -q` xanh + `head -30 CHANGELOG.md` mục 0.57.0 còn nguyên dưới 0.58.0
- [x] Q8 máy sạch lumen — `grep -i lumen ~/.claude/settings.json ~/.codex/config.toml`; `ls ~/.local/share/lumen ~/.config/lumen`; `ollama list`; `ls *.bak` của 2 file; khối CLAUDE.md
- [x] Q9 phát hành — `grep '"version"' .claude-plugin/plugin.json .codex-plugin/plugin.json` = 0.58.0; `grep -c "## 0.58.0" CHANGELOG.md` = 1
