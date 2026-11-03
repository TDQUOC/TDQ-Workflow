# Bản đồ phụ thuộc Lumen của TDQ — 2026-10-07

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Phạm vi: 51 file nhắc `lumen` ngoài `docs/`, `graphify-out/`, `claude-export/`, `.git`, `.tdq-worktrees/` (lệnh: `grep -rIl -i lumen --exclude-dir=…`). Bằng chứng chạy thật ở `docs/tdq/bench/2026-10-07-1843-hai-host-khong-lumen/` (viết tắt **HH**).

Xếp loại khi gỡ plugin + binary lumen, GIỮ ollama:
- **GÃY**: workflow dừng, sai, hoặc chấm lỗi oan.
- **ỒN**: vẫn chạy nhưng tốn lượt, in cảnh báo sai, tốn token hoặc chạy lại việc thừa.
- **ỔN**: tự rơi êm, không ai thấy khác biệt.
- **TĨNH**: chỉ là chữ/ghi chú/dữ liệu, không ảnh hưởng runtime (vẫn cần dọn khi gỡ hẳn).

## 1. Hook (chạy mỗi lượt)

| File:dòng | Vai trò | Claude Code | Codex | Bằng chứng |
|---|---|---|---|---|
| `hooks/scripts/search_gate.py:38` `TANG_KHAI_NIEM` + `ly_do_dung_xuong` | gate chặn grep trước tầng khái niệm; lumen là 1/3 tầng | **ỔN** về cơ chế: LSP/graphify vẫn mở khoá | **ỔN** về cơ chế — nhưng xem mục 5: hook Codex chưa thấy chạy | HH `claude-code.md`: chặn 2 lần, graphify mở khoá |
| `scripts/search_rules.py:79` `LOI_RA` | lời nhắc khi chặn: câu đầu "Ask first: lumen semantic_search …" | **ỒN**: agent đi tìm tool lumen không tồn tại (HH: 1 lượt `ToolSearch("lumen")` thừa) | **ỒN** (cùng chuỗi) | HH `claude-code.md` |
| `scripts/search_rules.py:585` `LUMEN` regex, `la_goi_khai_niem` | nhận diện lời gọi lumen | **ỔN** (không có lời gọi thì không khớp) | **ỔN** | đọc mã |
| `hooks/scripts/search_observe.py:7,74,86` | sổ lời gọi khái niệm | **TĨNH** (docstring) | **TĨNH** | đọc mã |
| `hooks/hooks.json:87` matcher `mcp__plugin_lumen_lumen__semantic_search\|mcp__lsp__.*\|Bash` | PostToolUse ghi sổ | **ỔN** (nhánh lumen không bao giờ khớp; Bash vẫn bắt graphify) | — | đọc mã |
| `.codex/hooks.json:42,53` matcher `.*lumen.*\|.*lsp.*` | Pre/PostToolUse ghi sổ (thay đổi CHƯA commit) | — | **ỔN** về matcher | đọc mã |
| `hooks/scripts/session_start.py:72` `TANG` + `can_khoi_tao:119-121` | dựng lại tầng tìm kiếm khi có tầng chưa sẵn sàng | **ỒN**: tầng lumen không bao giờ `san_sang` → mỗi phiên mở sau 6 giờ (`THU_LAI_GIAY`) lại chạy dựng nền `tdq_setup.py --nen` (cài thiếu, `graphify extract`, smoke) và in "[TDQ:SEARCH] Setting up the search layers…" | n/a (Codex không có SessionStart TDQ) | đọc mã `session_start.py:97-121` |

## 2. Script

| File:dòng | Vai trò | Kết quả khi lumen vắng | Loại | Bằng chứng |
|---|---|---|---|---|
| `scripts/tdq_lsp.py:452` `bac5_lumen` | bậc 5 thang kiểm | CẢNH BÁO, không chặn; nhưng gợi ý sai `lumen index <dự án>` (kiểm index trước, chưa hỏi binary có không) | **ỒN** | HH `script-tdq.md` |
| `scripts/tdq_lsp.py:788` `kiem_mot_lenh` (smoke 4 tầng) | dòng tổng của `tdq_lsp.py check` | **CHƯA ĐẠT vĩnh viễn, exit 4** — smoke luôn trượt tầng lumen; bước 1b của intake chạy lệnh này MỖI request | **ỒN** (sát GÃY: agent có thể coi là chặn và hỏi user mỗi lần) | HH `script-tdq.md` |
| `scripts/tdq_lsp.py:546` `_binary_lumen`, `:607` `_lumen_thieu_binary_windows` | bộ dò binary duy nhất | trả `""` | **ỔN** | HH |
| `scripts/tdq_lsp.py:859-880` `wake` | đánh thức ollama khi cần tìm lumen | vẫn bật ollama dù không còn ai dùng | **ỒN** nhẹ | đọc mã |
| `scripts/tdq_finish.py:176` `step_reindex` | reindex mỗi turn | `skip (lumen not installed)` | **ỔN** | HH `script-tdq.md` |
| `scripts/tdq_setup.py:162` `kiem_cau_hinh_lumen` | ghi nợ khi thiếu `~/.config/lumen/config.yaml` | nếu user xoá luôn config → mỗi lần setup ghi nợ "chưa có config lumen" | **ỒN** (khi xoá config) | đọc mã `tdq_setup.py:760` |
| `scripts/tdq_setup.py:273` `smoke_bon_tang` | smoke dùng chung | tầng lumen TRƯỢT | **ỒN** (cùng gốc với `kiem_mot_lenh`) | HH |
| `scripts/tdq_setup.py:676-693` dựng nền `lumen()` | index nền | log `nền: không thấy lumen — bỏ index` | **ỔN** | đọc mã |
| `scripts/tdq_setup.py:327` khối hướng dẫn ghim vào instruction user | chép luật 4 tầng có "Khái niệm mơ hồ → lumen" | **ỒN**: ghim lại câu nhắc tầng đã gỡ | đọc mã |
| `scripts/tdq_codex_mcp.py:107,131` `khai_mcp_codex` | khai MCP lumen cho Codex | thiếu binary → `skipped`; **mục cũ đã khai thì `already present, left unchanged`** — không bao giờ gỡ mục trỏ vào binary đã mất | **ỒN** (Codex vẫn khởi động, xem mục 5) | đọc mã + HH `codex.md` |
| `scripts/setup_status.py:56,245` + `setup_status_render.py:177` | trang trạng thái | `lumen: not installed`, vẫn in model/endpoint từ config sót | **ỔN** | HH `script-tdq.md` |
| `scripts/tdq_state.py:1194,1209` `PHASE_TABLE` (quick_analyze) | luật in ra `next` | "call mcp__lsp__* and lumen IN PARALLEL"; cấm "grepping … with no LSP+lumen attempt first" | **GÃY (chấm oan)**: không thể thử lumen → mọi grep ký hiệu ở lane nhanh thành vi phạm | đọc mã |
| `scripts/skill_tokens.py:70` | danh sách plugin ngoài | **TĨNH** | | |

## 3. Luật chữ trong skill (agent đọc và bị chấm theo)

| File:dòng | Câu luật | Loại khi gỡ lumen |
|---|---|---|
| `skills/tdq-intake/references/analyze-full.md:33-39` | "LSP and lumen together … A grep for a symbol with no LSP+lumen attempt first is a QC defect" | **GÃY (chấm oan)** |
| `skills/tdq-intake/references/quick-lane.md:42` | B1: "call `mcp__lsp__*` and lumen in parallel, merge both layers, grep last" | **GÃY (chấm oan)** |
| `skills/tdq-build/SKILL.md:66` | "LSP + lumen together, before grep, on every search of a code symbol" | **GÃY (chấm oan)** — có lối thoát chỉ cho LSP ("tools are missing → say so"), không cho lumen |
| `skills/tdq-build/references/rules/chung.md:81` | "one round of lumen or grep" | **ỔN** (có "or grep") |
| `skills/tdq-setup/references/uu-tien-tim-kiem.md` (8 chỗ) + `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md` (9) | bảng loại câu hỏi → tầng; đã có ngoại lệ "lumen unhealthy → agent-lsp then grep" | **ỒN** — đúng ý nhưng hàng "khái niệm mơ hồ → lumen" thành câu chết; cần viết lại hàng đó |
| `skills/tdq-setup/SKILL.md:3,10,44,72` + `references/lumen.md` | cài lumen, bậc 5 | **TĨNH** (hướng dẫn cài; giữ nếu muốn cài lại) |
| `skills/tdq-conventions/references/reminder-codes.md:23` | mô tả `TDQ:SEARCH` | **TĨNH** |
| `skills/tdq-conventions/references/phases.md:18` | bảng phase sinh từ PHASE_TABLE | đi theo `tdq_state.py` (GÃY cùng gốc) |
| `skills/tdq-conventions/references/plugin-routing.md:42` | "Log / trace observability → lumen" | **TĨNH**, nhưng **sai nghĩa sẵn** (lumen là tìm ngữ nghĩa code, không phải observability) — lỗi độc lập |
| `C:/Users/admin/.claude/CLAUDE.md` (toàn cục, ngoài repo) | "Khái niệm mơ hồ → lumen" | **ỒN** — agent mọi dự án được bảo dùng tầng không còn |

## 4. Test (20 file `tests/test_*.py` + `helper.py` + 1 fixture)

Đo: chạy 20 file test nhắc lumen hai lần — có binary và vá `_binary_lumen` rỗng qua `USERPROFILE` tạm (đã xác nhận `_binary_lumen()` trả `''`): **447 passed cả hai lần** (27 s). Test đã mock hết binary → gỡ lumen **không làm đỏ test nào**.

| Nhóm | File | Loại |
|---|---|---|
| Ghim chữ luật — sẽ ĐỎ khi sửa luật bỏ chữ "lumen" | `test_claude_md_core.py:133`, `test_luat_4_tang.py:34`, `test_tdq_setup_skill.py:56,134-137` | **TĨNH** nay; phải sửa cùng lúc với luật |
| Phụ thuộc trạng thái máy (ollama) | `test_finish_reindex.py` — không mock `_ollama_dang_chay`: ĐỎ khi ollama tắt (mốc 2026-10-07 lúc 18:5x), XANH khi ollama chạy (20:0x) | **ỒN** sẵn có — lỗi test, độc lập với việc gỡ |
| Mock binary/hành vi lumen | `test_tdq_lsp.py`, `test_bac_lumen_hieu_ung.py`, `test_setup_status.py`, `test_setup_status_render.py`, `test_tu_khoi_tao.py`, `test_tdq_setup.py`, `test_codex_mcp.py`, `test_mot_lenh_kiem.py`, `test_search_gate.py`, `test_search_observe.py`, `test_search_rules.py`, `test_codex_search_gate.py` | **ỔN** (xanh khi vắng binary) |
| Dữ liệu/ghi chú | `test_lumenignore.py`, `test_plugin_tiers.py`, `test_adapter_host.py`, `test_tdq_test.py`, `helper.py`, `fixtures/phien_excalidraw_tim.json` | **TĨNH** |

## 5. Ngoài repo (máy user)

| Chỗ | Khi gỡ plugin | Loại | Bằng chứng |
|---|---|---|---|
| `~/.codex/config.toml` `[mcp_servers.lumen]` trỏ `…/plugins/cache/…/lumen/0.0.42/bin/lumen-windows-amd64.exe` | trỏ vào file không còn. Codex **vẫn khởi động, không in lỗi nào về lumen**, server lumen lặng lẽ biến mất khỏi danh sách tool | **ỔN** khi chạy, **TĨNH** cần dọn | HH `codex.md` |
| `~/.claude/settings.json` env `OLLAMA_HOST`, `LUMEN_EMBED_MODEL` | vô hại | **TĨNH** | |
| `~/.config/lumen/config.yaml` | xoá đi → `kiem_cau_hinh_lumen` ghi nợ | **ỒN** nếu xoá | đọc mã |
| Hook SessionStart/PreToolUse của chính plugin lumen | biến mất cùng plugin — **bớt** ~13,5k token/299 lần chèn (đo `do-noi-bo` 2026-10-03) | **lợi** | `docs/tdq/research/2026-10-03-1101-do-noi-bo.md:183` |

## 6. File còn lại trong 51

`CHANGELOG.md` (11 dòng lịch sử), `.gitignore:25-26,43` (bỏ qua `.tdq-lumen-index`), `.lumenignore` (cấu hình index), `.pytest_cache/v/cache/nodeids` (cache) — **TĨNH**.

## Tổng

| Loại | Số điểm | Ở đâu |
|---|---|---|
| GÃY (chấm oan) | 4 | `tdq_state.py` PHASE_TABLE, `analyze-full.md`, `quick-lane.md`, `tdq-build/SKILL.md` |
| ỒN | 9 | `LOI_RA`, `session_start` dựng lại mỗi 6 giờ, `kiem_mot_lenh` CHƯA ĐẠT vĩnh viễn, bậc 5 gợi ý sai, `wake`, `kiem_cau_hinh_lumen`, khối ghim instruction, `uu-tien-tim-kiem*.md`, `khai_mcp_codex` để mục chết |
| ỔN | còn lại phần runtime | gate, reindex, setup_status, bộ dò binary, test |

Không điểm nào làm workflow **dừng chạy** hay **traceback**. "GÃY" ở đây là gãy về luật: workflow chấm agent theo một tầng không còn tồn tại.
