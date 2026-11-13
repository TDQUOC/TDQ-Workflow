# Báo Cáo Kiểm Toán & Chạy Thử E2E Phần 5: Hệ Thống 67 CLI Scripts, Search / Archify / DevTools & Pipeline TDQ-Workflow Trên Windows + Antigravity

> **Phạm vi kiểm toán:** Toàn bộ `scripts/*.py` tại `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\scripts` (thực đếm **67 tệp Python**, vượt mốc "43+ scripts"), kiểm tra môi trường máy Windows thực tế, đối chiếu tích hợp Antigravity (`~/.gemini/config/`, `chrome-devtools-plugin`, `transcript.jsonl`), chạy `pytest` cho nhóm kiểm thử tương thích host/Windows/portable, và thực thi **End-to-End (E2E) Pipeline thực tế** trên kho git giả lập `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub5_e2e_cli\demo_project`.
>
> **Tuân thủ Guardrails:** Không sửa bất kỳ byte nào trong `TDQ-Workflow`, `TDQ-Workflow-Antigravity`, hay `C:\Users\admin\.gemini\config\`. Toàn bộ chạy với `PYTHONDONTWRITEBYTECODE=1` và `-p no:cacheprovider`.

---

## 1. Kiểm Kê & Phân Nhóm Toàn Bộ 67 Scripts (`scripts/*.py`)

Tổng số tệp trong `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\scripts\`: **67 tệp `.py`** (**39.619 dòng mã Python**). Dưới đây là phân loại đầy đủ theo 8 phân hệ chức năng:

### 1.1. Phân hệ State, Pipeline & Timing (7 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_state.py` | 2.975 | Trái tim điều phối trạng thái (`docs/tdq/state.json` & `STATE.md`). Lệnh: `next`, `get`, `init <slug> <lane> [--bo-qua-lsp]`, `set k=v`, `approve <spec\|plan\|quick> [--mode] [--by] [--expected-sha] [--strict] [--bo-qua-do] [--bo-qua-archify]`, `pause`, `resume`, `eval-enable`, `lech add\|list\|duyet\|bac`, `reset`, `phases-doc`, `modes`. Chứa các cổng cứng: `_cong_lsp` (L2531), `_r14_gate` (L2057), `_archify_gate` (L2098), `_chan_spec_chua_duyet` (L2277), `_chan_worktree_con_mo` (L2291), `_chan_eval_plan_chua_co` (L2341), `_chan_eval_evidence_chua_co` (L2374), `_chan_report_thieu` (L2435). |
| `tdq_finish.py` | 337 | Gom sổ sách cuối lượt vào 1 lệnh: `khoa-token` -> `lint` (`doc_lint.py`) -> `worklog` (`docs/workinglog/YYYY-MM-DD.md`) -> `timing` (`tdq_timing.py close` khi về `idle`) -> `phase` (`tdq_state.py set phase=...`) -> `archify` (`mark_stale`) -> `graphify` (`graphify extract . --code-only`). |
| `tdq_checkstatus.py` | 695 | Khôi phục ngữ cảnh cho request đang dang dở (`report`), tổng hợp trạng thái cổng duyệt, tiến độ plan tick, worktree mở và hướng dẫn bước tiếp theo không mất dữ liệu. |
| `tdq_readiness.py` | 192 | Bộ nhớ đệm kiểm dò tĩnh (static probes có băm đầu vào), không bao giờ lưu kết quả phán quyết live readiness. |
| `step_audit.py` | 213 | Đo chi phí bước thực thi (layer 2 runtime) của phiên Claude Code: số `requestId` phân biệt, `tool_calls / turn`, số lần `Read` lặp cùng 1 tệp, median & p90 assistant-gap. |
| `tdq_timing.py` | 402 | Đo wall-time của từng request/phase và hợp nhất các khoảng thời gian đã xác thực từ host transcript vào `docs/tdq/timing.jsonl` (`close`). |
| `tdq_ten_lenh.py` | 156 | Nguồn sự thật duy nhất cho bảng bí danh lệnh Việt -> Anh (`BANG_DOI_TEN`), tên trình thông dịch Python đa nền tảng (`py -3` trên Windows vs `python3` trên POSIX, kiểm tra Microsoft Store stub `windowsapps`), và wrapper `chay_subprocess` gắn cờ `CREATE_NO_WINDOW` (`0x08000000`) chống nháy cửa sổ `conhost.exe` trên Windows (L135-L154). |

### 1.2. Phân hệ Tìm Kiếm 3 Tầng — Grep / LSP / Graphify (5 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_lsp.py` | 817 | Thang chẩn đoán 8 bậc cho `agent-lsp` + smoke test 3 tầng (`grep`, `LSP`, `graphify`). Lệnh: `check` (alias `kiem`), `module`, `kich-ban`, `ghi-kiem <module> <N>`. Exit codes: `0` (ĐẠT), `3` (thiếu bậc hành động 1-4, 6 nhóm B, 8), `4` (đạt bậc nhưng trượt smoke test). |
| `lsp_module.py` | 618 | Quét các module ngôn ngữ theo gốc cấu hình (`pyproject.toml`, `tsconfig.json`, ...), sinh kịch bản MCP thực chứng (`start_lsp` -> `open_document` -> `find_references`) và lưu sổ chứng thực tại `docs/tdq/.tdq-lsp-module.json`. Cung cấp `cong_init(cwd)` chặn `tdq_state.py init` nếu module chưa `DAT`. |
| `tdq_graphify.py` | 109 | Thực thi giao dịch trích xuất đồ thị mã nguồn `graphify` và kiểm chứng nguồn gốc (provenance) của `graphify-out/graph.json`. |
| `search_rules.py` | 1.128 | Bộ phân loại AST/regex cho lệnh tìm kiếm Bash/Grep/Glob theo đặc tả §3 (3 quy tắc), quyết định `allow`/`deny` và hướng dẫn chuyển sang LSP hoặc Graphify. |
| `search_replay.py` | 293 | Phát lại lịch sử tìm kiếm từ phiên đã ghi qua hàm quyết định của `search_rules.py` để kiểm chứng tỷ lệ chặn/cho phép. |

### 1.3. Phân hệ Archify Visual BA & Excalidraw Canvas (10 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_archify.py` | 1.322 | CLI Adapter điều phối Archify Visual BA: `check`, `render`, `open`, `bridge` (chuyển `graphify-out/graph.json` sang Archify JSON-IR + coverage sidecar), `test-bridge`, `sync-master`, `status`, `verify` (kiểm tra ràng buộc digest giữa Markdown và `.manifest.json`). |
| `archify_delivery.py` | 623 | Tự động dò tìm engine Archify (`C:\Users\admin\Documents\archify`), gọi Node CLI `finalize`, xử lý đặc thù quyền Admin trên Windows (`is_windows_elevated`) và kiểm tra biên nhận `browser-check`. |
| `archify_artifacts.py` | 1.111 | Quản lý vòng đời hiện vật kiến trúc (`manifest.json`, `status.json`, `mark_stale`, đóng gói bundle kiến trúc tổng thể `docs/architecture/index.html`). |
| `archify_model.py` | 780 | Xác thực lược đồ mô hình Archify JSON-IR (`schema_version: 2`) và đối chiếu bằng chứng mã nguồn (`evidence_kind`: `planned`, `working-tree`, `committed`, `partial`). |
| `canvas_draw.py` | 125 | Bộ công cụ vẽ hình học dùng chung cho tài liệu sản phẩm Excalidraw nhiều chương. |
| `canvas_a4_rebuild.py` | 383 | Dựng lại toàn bộ tài liệu sản phẩm Excalidraw theo khổ dọc A4 rộng `1240px`. |
| `canvas_a4_ch4_ch7.py` | 176 | Bố cục thủ công theo chiều dọc cho Chương 4 và Chương 7 trên trang A4 `1240px`. |
| `canvas_move_block.py` | 210 | Di chuyển một khối (block) sẵn có trên Excalidraw sang đúng chương mục tiêu. |
| `canvas_layout_apply.py` | 61 | Áp dụng di chuyển đồng loạt 5 khối cũ về đúng chương trong một lần ghi duy nhất. |
| `check_canvas_layout.py` | 339 | Kiểm tra hình học (chồng lấn, tràn lề, khoảng cách) của cảnh Excalidraw đa chương. |

### 1.4. Phân hệ Smart Test Runner, Process Isolation & Hermetic Receipts (7 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_test.py` | 1.533 | Smart Test Runner tính bán kính ảnh hưởng AST (`ban_kinh`): chọn test module bị chạm trực tiếp hoặc qua bao đóng bắc cầu ngược (`reverse transitive import closure`). Lệnh: `vung-cham`, `tron-bo`, `so`, `report`. Ghi sổ `.tdq-test.jsonl` và phát hiện bỏ sót bán kính (`bo-sot`). |
| `tdq_test_manifest.py` | 348 | Thu thập danh sách test case (`collection.json` / pytest sidecar) và đối soát tính toàn vẹn tập case trước/sau khi chạy. |
| `tdq_test_process.py` | 401 | `IsolatedJob`: cô lập cây tiến trình chạy test (Windows Job Objects / process group) và thư mục tạm mà không làm bẩn `HOME`/`USERPROFILE` của tiến trình gọi. |
| `tdq_test_receipt.py` | 657 | Cơ chế biên nhận tái sử dụng kết quả test (`--reuse auto`) theo nguyên tắc **default-deny**: yêu cầu `docs/tdq/reuse-policy.json` khai báo tường minh `hermetic`, `input_paths`, `no_network`, `no_live_clock`, `no_personal_config` và `proof`, băm toàn bộ cây mã nguồn + runtime Python + gói cài đặt + biến môi trường (không lưu giá trị secret), khóa file `guard.lock` kèm kiểm tra Windows PID creation time (`GetProcessTimes`). |
| `tdq_test_result.py` | 519 | Bộ chuyển đổi bảo thủ cho báo cáo JUnit XML của `pytest` và `unittest` sang định dạng kết quả chuẩn hóa có băm `TDQ_RESULT`. |
| `tdq_test_report.py` | 383 | Tổng hợp thời lượng thực thi (Top 20 case/module chậm nhất) và xuất báo cáo ngoại tuyến JSON / Markdown / HTML gắn chặt với nguồn kết quả. |
| `tdq_vungfile.py` | 234 | Hàng rào vùng tệp cho phép sửa (`vung_file`), vùng khóa (`vung_khoa`) và mốc hoàn tác (undo mark) phục vụ chế độ `codex implement`. |

### 1.5. Phân hệ Team / Worktree / TCAS & Multi-Agent (5 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_team.py` | 1.782 | Điều phối chế độ đội (`implement_mode=subagent`): `assign` (lập bản đồ `docs/tdq/team/<slug>.json`), `audit`, `wave` (xếp đợt theo đồ thị `Cần:` và tách vùng tệp xung đột), `open` (mở nhánh + git worktree tại `.tdq-worktrees/<slug>/<task>` + nối NTFS Junction `.venv`/`node_modules` trên Windows), `check` (thử `git merge-tree` không chạm working tree + chạy lệnh `Test:` độc lập), `merge` (`rebase` + `merge --no-ff` + tự dọn worktree), `sweep [--clean]`, `clean`, `resolve`. |
| `tdq_worktree_registry.py` | 331 | Sổ cái đơn nguồn sự thật (`docs/tdq/worktrees.json` & `worktrees.md`) theo dõi mọi worktree mở/đóng trên toàn dự án; khóa cổng chuyển sang `phase=qc` nếu còn dòng đang mở. |
| `scan_block_symbols.py` | 118 | Quét các ký hiệu Unicode/non-ASCII trong các khối văn bản giao tiếp với người dùng. |
| `tdq_codex.py` | 904 | Lớp bọc thực thi `codex exec` cho chế độ `codex implement`, kiểm soát vùng tệp và thu hồi thay đổi vi phạm. |
| `tdq_codex_mcp.py` | 325 | Khai báo máy chủ MCP `lsp` vào `~/.codex/config.toml` và cài cổng chặn tìm kiếm vào `.codex/hooks.json`. |

### 1.6. Phân hệ DevTools MCP & Visual Regression Diff (2 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_devtool_mcp.py` | 330 | Quản lý Chrome DevTools MCP (`chrome-devtools` trên cổng CDP `127.0.0.1:9222`): kiểm tra cấu hình (`check_devtool_setup`), tự động đăng ký vào `~/.claude.json` & `~/.claude/settings.json` (`setup`), và phóng Chrome ngầm với `ChromeDevProfile` riêng biệt (`launch`). |
| `tdq_vision_diff.py` | 725 | Động cơ so sánh hồi quy thị giác bằng `Pillow` (`PIL`): tải ảnh thiết kế từ `--source` hoặc `--figma-url` (qua `FIGMA_TOKEN`), chuẩn hóa khung Letterbox không méo tỷ lệ, che vùng động (`--ignore-boxes`), gom cụm ô sai khác `[1], [2]...`, xuất `diff_highlight.png`, `metrics.json`, báo cáo `.md` và trang `.html` tương tác (Split Slider, Onion-Skin, Blink 2Hz). |

### 1.7. Phân hệ Setup, Portable Bundle, Transcript, Token, Knowledge/Harvest & Lint (24 scripts)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_setup.py` | 2.019 | Cài đặt và kiểm chứng toàn bộ phụ thuộc tìm kiếm (tải `agent-lsp` kiểm SHA256, khai MCP `lsp`, cài `graphify`, đồng bộ `.mcp.json` cache plugin Claude, đồng bộ Codex MCP, cài shim `python3` trên Windows, chạy nền cập nhật bù). |
| `setup_status.py` | 480 | Thu thập trạng thái cài đặt thực tế của TDQ-Workflow trên máy hiện tại thành cấu trúc dữ liệu chuẩn. |
| `setup_status_render.py` | 251 | Kết xuất dữ liệu từ `setup_status.py` thành một trang HTML độc lập (self-contained) để chẩn đoán trực quan. |
| `build_portable.py` | 814 | Xây dựng gói plugin cho Antigravity (`--sinh-agy` -> `antigravity_portable/`, viết lại `${CLAUDE_PLUGIN_ROOT}` thành đường dẫn tuyệt đối `~/.gemini/config/plugins/tdq-workflow`, sinh `plugin.json`, `hooks.json`, `mcp_config.json`, `manifest.json`), viết lại `hooks/hooks.json` hoặc phát hành nhánh `main`. |
| `tdq_checkportable.py` | 630 | Kiểm tra tính toàn vẹn SHA256 của gói portable trên máy đích (`check`), vá tệp cấu hình thiếu (`setup`), và cài đặt shim `python3.cmd` / `python3` đứng trước Microsoft Store stub trên Windows (`setup --shim`). |
| `claude_export.py` | 622 | Đóng gói và kiểm tra gói xuất cấu hình Claude Code để mang sang máy khác. |
| `plugin_tiers.py` | 213 | Quản lý phân tầng plugin cấp người dùng của Claude Code. |
| `tdq_transcript.py` | 547 | Đọc transcript của Claude Code (`~/.claude/projects/<slug>`) và Codex (`~/.codex/sessions`) thành các khoảng thời gian (`api`, `tool`, `job`) đã kiểm chứng mà không ghi vào state. |
| `tdq_transcript_cache.py` | 195 | Bộ đệm cục bộ theo request cho dấu vết transcript đã chuẩn hóa (không lưu nội dung tin nhắn thô, tự giới hạn dung lượng và tuổi). |
| `token_audit.py` | 528 | Đo chi phí token thực tế (carry-cost = kích thước output × số lần gọi API còn lại sau đó, cộng quy đổi ảnh theo ô `28×28 px`) của phiên Claude Code bằng `anthropic-tokenizer`. |
| `token_budget.py` | 175 | Khóa số đo token của từng tệp quy tắc vào `docs/tdq/token-budget.json` để CI và `doc_lint` R13 cưỡng chế trần ngân sách. |
| `skill_tokens.py` | 361 | Bộ đếm token thực cho tập `skills/` qua môi trường ảo `.venv-tokens` (`anthropic-tokenizer`); cấm ước lượng `chars/4` (thiếu thư viện -> thoát mã `3`). |
| `context_surface.py` | 363 | Đo bề mặt ngữ cảnh (context surface) của plugin TDQ-Workflow theo đúng cách LLM nạp vào bộ nhớ. |
| `skill_inventory.py` | 329 | Kiểm kê danh mục skills hiện có trên đĩa phục vụ bước B0 của `tdq-intake`. |
| `skill_router.py` | 221 | Kho tra cứu định tuyến skill nguyên mẫu (prototype) giúp chọn đúng vài skill liên quan thay vì nạp tràn. |
| `doc_lint.py` | 913 | Kiểm tra quy chuẩn tài liệu hướng dẫn và hồ sơ TDQ (R1–R15, bao gồm R13 khóa token và R14 bắt buộc ngưỡng số học trong Spec §6 phải có `Đo trước` & `Dự phòng nếu trượt`). |
| `doc_dup.py` | 239 | Phát hiện các đoạn văn bản bị lặp lại giữa các tệp tài liệu quy tắc mà LLM đọc. |
| `doc_index.py` | 314 | Ghi mục lục dòng tự động (`<!-- muc-luc-dong: ... -->`) vào đầu các tệp quy tắc dài để agent đọc từng mục theo phạm vi dòng. |
| `i18n_check.py` | 192 | Quét phát hiện các dòng mã/tài liệu còn sót tiếng Việt chưa gắn cờ `# i18n-allow`. |
| `luat_phan_loai.py` | 153 | Gợi ý nhãn phân loại cho từng mỏ neo quy tắc: `ly-luan` (reasoning) hoặc `user-facing`. |
| `kiem_no_marker.py` | 138 | Kiểm tra sổ cái các dấu hiệu nợ (`debt markers`) do bộ quy tắc gọn để lại trong mã nguồn. |
| `tdq_no.py` | 54 | Ghi nhận nợ phụ thuộc (`docs/tdq/no-phu-thuoc.md`) cho những công cụ mà `tdq_setup.py` không thể tự cài đặt. |
| `tdq_harvest.py` | 258 | Quét nhật ký làm việc (`docs/workinglog/*.md`) theo mẫu `Lỗi/Bug/Issue ... Khắc phục/Fix/Resolution` để trích xuất bài học vào vùng cách ly `docs/tdq/knowledge/candidates/` (`scan`, `list`, `approve`, `reject`). |
| `tdq_knowledge.py` | 196 | Kiểm định bài học tri thức theo hợp đồng O12 (`check`): quét rò rỉ khóa bí mật (`SECRET_PATTERNS`) và kiểm tra vòng đời YAML frontmatter (`candidate`, `reviewed`, `rejected`, `superseded`). |
| `utf8_io.py` | 109 | Ép `sys.stdout` / `sys.stderr` sang `UTF-8` ngay khi import để tiếng Việt trên Windows (`cp1252`) không bao giờ gây `UnicodeEncodeError`. |

### 1.8. Phân hệ Đánh Giá Thực Nghiệm & Benchmark (6 scripts — bổ sung ngoài danh sách gợi ý để đủ 100% 67 tệp)
| Script | Số dòng | Chức năng cốt lõi & Subcommands / API |
|---|---:|---|
| `tdq_bench.py` | 823 | So sánh định lượng giữa `mode main` và `mode subagent` (`gen-plan`, `calibrate`, `simulate`, `scan`). |
| `tdq_runtime_bench.py` | 987 | Khung chạy thực nghiệm thời gian chạy hữu hạn có lưu bằng chứng và kiểm chứng bảo thủ. |
| `tdq_eval.py` | 1.922 | Đánh giá A/B hai nhánh skill tuân thủ luật TDQ bằng con số thực nghiệm (`setup`, `run`, `score`, `report`). |
| `tdq_eval_contract.py` | 569 | Hợp đồng thuần (pure functions) cho Eval: phân loại target (`classify_targets`), kiểm tra `eval-plan` và cổng `check_eval_gate`. |
| `tdq_eval_hosts.py` | 579 | Bộ điều hợp thực thi đánh giá tự động cho Claude Code và Codex trên Windows. |
| `tdq_skill_eval.py` | 717 | Điểm vào CLI cho đánh giá chất lượng skill/plugin (O2: `plan`, `run`, `report`). |

---

## 2. Kiểm Tra Môi Trường Máy Windows & Các Khoảng Trống Tích Hợp Antigravity

### 2.1. Kết quả kiểm tra công cụ & Health Checks thực tế (Non-destructive)

| Lệnh kiểm tra | Exit Code | Đầu ra thực tế trên máy |
|---|---:|---|
| `python --version` | `0` | `Python 3.13.15` (`C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe`) |
| `python3 --version` | `0` | `Python 3.13.15` (ĐÃ CÓ shim `python3` / `python3.cmd` tại `C:\Users\admin\AppData\Local\agy\bin\python3.cmd`, `C:\Users\admin\.cargo\bin\python3.cmd`, `...\Python313\Scripts\python3.cmd` đứng TRƯỚC `WindowsApps\python3.exe`!) |
| `py --version` | `0` | `Python 3.13.15` |
| `node --version` | `0` | `v24.21.0` |
| `where.exe agent-lsp` | `0` | `C:\Users\admin\.local\bin\agent-lsp.exe` (phiên bản `0.19.2`) |
| `where.exe graphify` | `0` | `C:\Users\admin\AppData\Local\Programs\Python\Python313\Scripts\graphify.exe` |
| `where.exe pyright` | `0` | `C:\Users\admin\AppData\Roaming\fnm\aliases\default\pyright.cmd` |
| `where.exe pytest` | `0` | `C:\Users\admin\AppData\Local\Programs\Python\Python313\Scripts\pytest.exe` (pytest `9.1.1`) |
| `python -c "import PIL..."` | `0` | `PIL: 13.0.0` (`tdq_vision_diff.py` đủ thư viện Pillow) |
| `tdq_archify.py check` | `0` | `{"node_ok": true, "node_version": "v24.21.0", "archify_root": "C:\\Users\\admin\\Documents\\archify", "ready": true, "error": null}` |
| `tdq_checkportable.py check` | `0` | `NOTE không thấy bundle ở đây — repo này tự là plugin... cần layout Antigravity thì sinh bằng: python3 scripts/build_portable.py --sinh-agy` |
| `tdq_lsp.py check` (trên `TDQ-Workflow-Antigravity` rỗng) | `4` | `7/8 bậc ĐẠT` (cảnh báo Bậc 7 chưa có đồ thị `graphify`), trượt smoke `grep` & `graphify` vì thư mục rỗng chưa có mã nguồn. |
| `TDQ_PROJECT_DIR=...\TDQ-Workflow python tdq_lsp.py check` | `3` | `6/8 bậc ĐẠT · smoke 3/3 tầng trả lời được` (`grep` ĐẠT, `LSP` ĐẠT, `graphify` ĐẠT); Bậc 7 cảnh báo đồ thị cũ hơn mã nguồn 725 phút; Bậc 8 `THIẾU (python:. HET_HAN)` nên trả về `EXIT: 3`. |
| `tdq_devtool_mcp.py` | `0` | `{"mcp_registered": true, "permission_allowed": true, "chrome_available": true, "profile_exists": true, "cdp_listening": true, "all_ready": true}` (đọc từ `~/.claude.json` và cổng `9222`). |

> **Lưu ý nhỏ về CLI `tdq_lsp.py`:** `tdq_lsp.py check` **không nhận cờ `--project`** (truyền `--project` bị báo `unrecognized arguments` với `EXIT: 2`), mà đọc biến môi trường `TDQ_PROJECT_DIR` hoặc tự dò ngược `.git` từ `cwd` (`tdq_lsp.py:208-221`).

---

### 2.2. Khoảng trống #1: `tdq_setup.py` & `build_portable.py` KHÔNG đăng ký MCP `lsp` cho Antigravity

Qua kiểm tra mã nguồn trực tiếp và cấu hình thực tế trên đĩa:
1. **`tdq_setup.py` chỉ ghi cấu hình MCP cho Claude Code và Codex:**
   - Ghi `mcpServers.lsp` vào `~/.claude.json` (`khai_server_mcp`, `tdq_setup.py:338-385`).
   - Đồng bộ sang `<claude_plugin_cache>/.mcp.json` và thêm quyền `mcp__lsp__*`, `mcp__plugin_tdq-workflow_lsp__*` vào `~/.claude/settings.json` (`dong_bo_mcp_plugin_cache`, `tdq_setup.py:648-695`).
   - Khai báo cho Codex vào `~/.codex/config.toml` và `.codex/hooks.json` qua `tdq_codex_mcp.py` (`tdq_setup.py:1538-1546, 1893-1909, 1997-2002`).
   - **Hoàn toàn không có bất kỳ dòng mã nào** đọc/ghi `C:\Users\admin\.gemini\config\mcp_config.json` (tệp này trên máy hiện đang rỗng `0 byte`, gây `JSONDecodeError` nếu đọc thẳng) hay `C:\Users\admin\.gemini\config\plugins\tdq-workflow\mcp_config.json`.
2. **`build_portable.py --sinh-agy` cũng bỏ sót máy chủ MCP `lsp`:**
   - Tại `build_portable.py:89` và `tdq_checkportable.py:62, 143-155`, hằng số `MCP_SERVERS` chỉ chứa `("tavily-primary", "tavily-backup")`.
   - Kiểm tra tệp đã cài thực tế `C:\Users\admin\.gemini\config\plugins\tdq-workflow\mcp_config.json` và thư mục schema `C:\Users\admin\.gemini\antigravity\mcp\`: chỉ có `tdq-workflow_tavily-primary` và `tdq-workflow_tavily-backup`, **không hề có máy chủ `lsp`**.
   - **Hệ quả nghiêm trọng trên Antigravity:** Khi chạy `tdq_state.py init <slug> full` trên một dự án có mã nguồn, cổng `_cong_lsp` (`tdq_state.py:2531-2561`) chặn lại với `EXIT: 2` và yêu cầu agent gọi các công cụ MCP `mcp__lsp__start_lsp`, `mcp__lsp__open_document`, `mcp__lsp__find_references` rồi chạy `tdq_lsp.py ghi-kiem`. Nhưng trên Antigravity, agent **không hề có công cụ `mcp__lsp__*`** (trừ khi tự cấu hình thủ công ngoài luồng), buộc mọi phiên trên Antigravity phải lách qua `--bo-qua-lsp "<lý do>"`!
   - Đồng thời trong `C:\Users\admin\.gemini\config\config.json`, plugin `tdq-workflow` hiện đang ở trạng thái `{"enabled": false}`.

---

### 2.3. Khoảng trống #2: Xung đột / Trùng lặp giữa `tdq_devtool_mcp.py` (`tdq-browser-*`) với `chrome-devtools-plugin` và `browser` Subagent của Antigravity

| Khía cạnh | TDQ-Workflow (`tdq_devtool_mcp.py` + `tdq-browser-research` / `tdq-browser-test`) | Antigravity Native (`chrome-devtools-plugin` v1.10.1 + `browser` subagent) | Hệ quả & Mức độ tương thích |
|---|---|---|---|
| **Cấu hình cài đặt** | `tdq_devtool_mcp.py:183-248` chỉ ghi vào `~/.claude.json` và `~/.claude/settings.json` với `--browserUrl=http://127.0.0.1:9222` và thư mục `~/ChromeDevProfile`. | Cài qua Agent Marketplace tại `C:\Users\admin\.gemini\config\plugins\chrome-devtools-plugin\`; tự khởi chạy Chrome bằng profile bền vững riêng của plugin. | `tdq_devtool_mcp.py setup` không có tác dụng trên Antigravity; `tdq_devtool_mcp.py launch` mở thêm một tiến trình Chrome rời ở cổng `9222` song song với webview/Chrome của Antigravity. |
| **Tiền tố tên công cụ MCP** | Các skill `tdq-browser-research/SKILL.md` (L30-47) và `tdq-browser-test/SKILL.md` (L28-58) viết cứng tiền tố chuẩn Claude Code: `mcp__chrome-devtools__navigate_page`, `mcp__chrome-devtools__evaluate_script`, `mcp__chrome-devtools__take_snapshot`, `mcp__chrome-devtools__take_screenshot`, `mcp__chrome-devtools__resize_page`, `mcp__chrome-devtools__hover`, `mcp__chrome-devtools__fill_form`, `mcp__chrome-devtools__click`, `mcp__chrome-devtools__list_console_messages`, `mcp__chrome-devtools__list_network_requests`, `mcp__chrome-devtools__get_css_styles`, `mcp__chrome-devtools__list_pages`. | Trong Antigravity, công cụ MCP được đăng ký với một dấu gạch dưới `mcp_<serverName>_<toolName>` (không phải hai dấu `__` như Claude Code!). Tên hàm gốc của `chrome-devtools-mcp` (`navigate_page`, `take_snapshot`, `take_screenshot`, `evaluate_script`, `get_css_styles`, `click`, `list_pages` — xem `chrome-devtools/SKILL.md:14-38`) **trùng khớp 100%**, nhưng khác quy ước tiền tố (`mcp_...` vs `mcp__chrome-devtools__...`) và yêu cầu tham số `pageId` bắt buộc trên các bản `chrome-devtools-mcp` mới. | Agent trên Antigravity đọc `tdq-browser-*` sẽ tìm tên tool `mcp__chrome-devtools__*` không tồn tại, và dễ bỏ sót tham số `pageId` bắt buộc của `chrome-devtools` v1.10.1. |
| **Định tuyến tác vụ trình duyệt** | Yêu cầu agent chính chạy lệnh shell `python3 scripts/tdq_devtool_mcp.py launch` rồi trực tiếp gọi MCP. | Kiến trúc hệ thống của Antigravity quy định mọi tương tác trang web trực quan phải ủy quyền ngay lập tức cho subagent `browser` (hoặc dùng skill `chrome-devtools` khi gỡ lỗi DevTools chuyên sâu), không tự chạy script phóng trình duyệt ngoài. | Trùng lặp chồng chéo vai trò với subagent `browser` có sẵn của Antigravity và các skill chuyên sâu (`a11y-debugging`, `debug-optimize-lcp`, `cookie-debugging`, `memory-leak-debugging`). |

---

### 2.4. Khoảng trống #3: Bất tương thích hoàn toàn về Đường dẫn & Schema JSONL giữa `tdq_transcript.py` / `token_audit.py` / `step_audit.py` và Transcript của Antigravity

Đã đối chiếu trực tiếp mã nguồn (`tdq_transcript.py`, `token_audit.py`, `step_audit.py`) với tệp transcript thực của phiên Antigravity hiện tại tại `C:\Users\admin\.gemini\antigravity\brain\3b9ddf2b-58ed-4fbd-86f1-72cd99655459\.system_generated\logs\transcript.jsonl` và chạy thực nghiệm cả 3 công cụ:

| Thuộc tính | TDQ-Workflow mong đợi (Claude Code / Codex) | Thực tế của Antigravity (`transcript.jsonl`) |
|---|---|---|
| **Đường dẫn lưu trữ** | `~/.claude/projects/<project-slug>/*.jsonl` (`tdq_transcript.py:58-62`) hoặc `~/.codex/sessions/**/*.jsonl` (`L110`). | `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl` (kèm `transcript_full.jsonl` và các mảnh `chunks\transcript\00000000.jsonl`). Không gắn slug dự án vào tên thư mục. |
| **Trường phân loại bản ghi (`type`)** | Claude: `{"api-request", "assistant", "user", "system", "progress"}` (`L25`); Codex: `{"session_meta", "response_item", "event_msg", "turn_context"}` (`L26`). | `USER_INPUT`, `SYSTEM_MESSAGE`, `PLANNER_RESPONSE`, `GENERIC` (cùng trường `source`: `USER_EXPLICIT`, `MODEL`, `SYSTEM` và `step_index`, `status`). |
| **Trường thời gian** | `record["timestamp"]` (`tdq_transcript.py:277`, `step_audit.py:107`). | `record["created_at"]` (ví dụ `"2026-11-13T06:13:58Z"`). |
| **Định danh dự án & phiên** | `record["cwd"]` + `record["sessionId"]` (Claude) hoặc `payload["cwd"]` + `payload["id"]` (Codex). | Không có trường `cwd` hay `sessionId` trong từng dòng JSONL; ID hội thoại nằm ở tên thư mục cha `<conversation-id>`. |
| **Cấu trúc Tool Calls** | Claude: `message.content[]` chứa `{"type": "tool_use", "id": ..., "name": "Read", "input": ...}` và `{"type": "tool_result", "tool_use_id": ...}`. | Trong bước `PLANNER_RESPONSE`: mảng `tool_calls: [{"name": "run_command", "args": {...}}]`; kết quả tool nằm ở các bước `GENERIC` kế tiếp trong trường chuỗi `content` (có `truncated_fields`). |
| **Thống kê Token** | Claude: `record["message"]["usage"]` (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, ...). | Đặt thẳng ở cấp cao nhất của bản ghi `PLANNER_RESPONSE`: `input_tokens`, `cache_read_tokens`, `output_tokens`. |

**Bằng chứng chạy thực tế trên thư mục log của Antigravity (`EXIT: 0` nhưng dữ liệu bằng 0 / từ chối schema):**
- `python scripts/step_audit.py --transcript-dir "...\.system_generated\logs"`: đọc cả `transcript.jsonl` và `transcript_full.jsonl` (đếm nhầm thành `2 session(s)`!) và in `Model steps: 0 | Tool calls per turn: 0.00 (0 turn(s))`.
- `python scripts/token_audit.py --transcript-dir "...\.system_generated\logs"`: in `API call: 0 · tool call: 0 · total carry-cost 0 tokens`.
- `tdq_transcript.read_transcripts(..., transcript_dir="...\.system_generated\logs")`: quét đệ quy luôn cả các mảnh trong `chunks/` (10 tệp), đánh dấu toàn bộ 10/10 nguồn là `"status": "unavailable", "reason": "unrecognized_schema"` với `"counters": {"unknown_events": 69}` (và `malformed_lines` trên các mảnh cắt chunk), trả về `spans_count: 0`, `quality: unavailable (no_usable_source)`.

---

### 2.5. Kiểm toán lời gọi `python3` vs `python` / `py -3` trên Windows across Skills / Hooks / Scripts

Quét toàn bộ cây mã nguồn `TDQ-Workflow` (không tính dòng shebang `#!/usr/bin/env python3` ở dòng 1):
- **`skills/`:** **38 tệp** có chứa lệnh `python3` (**125 vị trí**), ví dụ `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" ...`.
- **`hooks/`:** **8 tệp** có chứa `python3` (**30 vị trí**), nhưng trong `hooks/hooks.json` gốc của Claude Code, **100% lệnh hook đã có chuỗi dự phòng đa nền tảng**: `python3 "..." || py -3 "..." || python "..."` (được kiểm chứng bởi `test_auto_fix_python3_hook.py`).
- **`scripts/`:** **33 tệp** có chứa chuỗi `python3` (**207 vị trí** — chủ yếu trong docstring và văn bản hướng dẫn in ra cho agent/user).
- **Cơ chế xử lý của TDQ trên Windows hoạt động như thế nào?**
  1. Trong bản đóng gói Antigravity (`C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json`, sinh bởi `build_portable.py --sinh-agy` trên Windows), lệnh hook được viết thẳng thành `py -3 "C:\Users\admin\.gemini\config\plugins\tdq-workflow/hooks/scripts/agy_pretooluse_gate.py"` (`tdq_ten_lenh.py:88` -> `LENH_PYTHON_WINDOWS = "py -3"`).
  2. Trong `tdq_team.py:1176-1196` (`chuan_hoa_lenh_test`), nếu dòng `Test:` trong `plan.md` viết `python3 -m pytest ...`, hàm tự động thay token đầu `python3` bằng chính `sys.executable` trước khi chạy subprocess trong worktree.
  3. Trên máy Windows mới chưa chạy `tdq_setup.py` / `tdq_checkportable.py setup --shim`, gõ `python3` theo văn bản trong `skills/` sẽ kích hoạt stub Microsoft Store (`C:\Users\admin\AppData\Local\Microsoft\WindowsApps\python3.exe`, thoát mã `49` / `9009`). Tuy nhiên trên máy kiểm toán hiện tại, shim `python3.cmd` đã được cài sẵn trên `PATH` (bao gồm cả `C:\Users\admin\AppData\Local\agy\bin\python3.cmd` của chính Antigravity CLI!), nên cả `python3`, `python`, và `py -3` đều trả về `Python 3.13.15` (`EXIT: 0`).

---

## 3. Kết Quả Chạy Pytest Trên Bộ Kiểm Thử Tương Thích Host / Antigravity / Windows Của TDQ-Workflow

Thực thi không ghi cache (`PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider -q`) trên **11 tệp test chuyên biệt**:
- `tests/test_agy_hooks.py`
- `tests/test_sinh_agy.py`
- `tests/test_build_portable.py`
- `tests/test_checkportable.py`
- `tests/test_shim_python3.py`
- `tests/test_auto_fix_python3_hook.py`
- `tests/test_an_cua_so_windows.py`
- `tests/test_hook_windows.py`
- `tests/test_tuong_thich_host.py`
- `tests/test_adapter_host.py`
- `tests/test_devtool_mcp_integration.py`

**Kết quả thực tế:**
```text
151 passed, 242 subtests passed in 22.28s
EXIT: 0
```

---

## 4. Thực Thi Mô Phỏng Pipeline End-to-End (E2E) Trong Kho Scratch `demo_project`

**Thư mục dự án mô phỏng:** `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\sub5_e2e_cli\demo_project`
**Cấu trúc dự án:** Kho `git init -b main` gồm `pyproject.toml`, 2 module Python (`scripts/calc.py`, `scripts/formatter.py`) và 2 tệp kiểm thử (`tests/test_calc.py`, `tests/test_formatter.py`). Request slug: `2026-11-13-1325-demo-calc` (lane `full`).

### Bảng Tổng Hợp Từng Bước Thực Thi E2E & Mã Thoát Thực Tế

| Bước | Lệnh CLI thực thi | Exit Code | Kết quả & Minh chứng cổng kiểm soát (Gates) |
|---|---|---:|---|
| **1A. Khởi tạo khi chưa chứng thực LSP** | `python tdq_state.py init 2026-11-13-1325-demo-calc full` | **`2`** | **Cổng `_cong_lsp` chặn đúng thiết kế:** `LSP is not proven for every module of this project — init refused: python:. -> CHUA_KIEM`. |
| **1B. Kiểm tra module & sinh kịch bản LSP** | `python tdq_lsp.py module` / `python tdq_lsp.py kich-ban` | `3` / `0` | Phát hiện `python:. (4 file · pyproject.toml · CHUA_KIEM)` và in kịch bản 4 bước MCP cho symbol `format_sum (scripts\formatter.py:4)`. |
| **1C. Ghi chứng thực LSP & Khởi tạo lại** | `python tdq_lsp.py ghi-kiem "python:." 2` -> `python tdq_state.py init 2026-11-13-1325-demo-calc full` | **`0`** / **`0`** | Ghi `docs/tdq/.tdq-lsp-module.json` (`python:. -> DAT`); `init` mở request thành công: `✅ init: request=2026-11-13-1325-demo-calc lane=full phase=idle`. |
| **2A. Chuyển sang Analyze & Spec** | `python tdq_state.py set phase=analyze` -> tạo `brief` & `spec` -> `set phase=spec spec_file=docs/tdq/spec/2026-11-13-1325-demo-calc.md` | **`0`** | Tạo `docs/tdq/brief/2026-11-13-1325-demo-calc.md` và `docs/tdq/spec/2026-11-13-1325-demo-calc.md`. |
| **2B. Thử duyệt Spec trước khi render Archify** | `python tdq_state.py approve spec --by "duyệt spec"` | **`1`** | **Cổng `_archify_gate` chặn cứng** (do slug `>= 2026-11-09-0143`): `Refusal: docs/tdq/spec/2026-11-13-1325-demo-calc.md Archify preview/flow is missing or not current (status: invalid) - Manifest not found`. |
| **2C. Trích xuất Graphify & Bridge sang Archify** | `graphify extract . --code-only` -> `python tdq_archify.py bridge --graph graphify-out/graph.json --out docs/tdq/artifacts/bridged.json` | **`0`** / **`0`** | Sinh `graphify-out/graph.json` (`12 nodes, 14 edges, 3 communities`), chuyển đổi thành công sang `bridged.json` + `bridged.coverage.json` (`test-bridge` cũng `EXIT: 0`). |
| **2D. Render Archify Preview HTML thật & Verify** | `python tdq_archify.py render --type workflow --candidate ... --out docs/tdq/spec/2026-11-13-1325-demo-calc-preview.html --document ...` -> `tdq_archify.py verify ...` | **`0`** / **`0`** | Engine Node Archify chạy thật trong `2977 ms`, xuất tệp HTML độc lập `806.146 bytes`, vượt qua cả 4 cổng (`validate: pass`, `deliver: pass`, `check: pass`, `browser-check: pass`), sinh `.manifest.json` & `.receipt.json`. Lệnh `verify` trả về `"status": "current", "valid": true`. |
| **3A. Kiểm tra khóa băm SHA256 sai** | `python tdq_state.py approve spec --by "duyệt spec" --expected-sha 0000...0000 --strict` | **`2`** | **Khóa SHA256 chặn chính xác:** `Approval hash mismatch: expected 0000..., computed 6a46919d133b6a9a786bcc50818b01181378bc057f1a02853fa2078bb96052fd`. |
| **3B. Duyệt Spec với SHA256 thật & `--strict`** | `python tdq_state.py approve spec --by "duyệt spec" --expected-sha 6a46919d... --strict` | **`0`** | Lưu `spec_sha256` và `spec_descriptor` với `"assurance": "cli-verified", "version": 1`. |
| **4A. Lập Plan 3 tasks & Duyệt Plan (`subagent`)** | `set phase=plan plan_file=...` -> `approve plan --mode subagent --by "ok plan, mode subagent" --expected-sha <sha> --strict` | **`0`** / **`0`** | Khóa `plan_sha256`, chuyển thẳng sang `phase=implement` với `implement_mode=subagent`. (`tdq_state.py modes` báo `[o] main`, `[o] subagent`, `[x] codex`). |
| **4B. Phân công đội & Xếp đợt (`tdq_team.py`)** | `python tdq_team.py assign` -> `audit` -> `wave` | **`0` / `0` / `0`** | Ghi `docs/tdq/team/2026-11-13-1325-demo-calc.json`: giao `2/3 task` (`T1.1`, `T1.2`) thành `2 wave(s)`; giữ lại `T1.3` (`README.md`) cho leader (`KEPT T1.3 — vung-khoa` vì đường dẫn gốc không chứa dấu `/`). `wave` mở `Ready: T1.1` và giữ `HELD T1.2 — waiting on unfinished task(s): T1.1`. Thử `open T1.3` bị từ chối đúng luật (`EXIT: 1`). |
| **4C. Mở Worktree thật & Kiểm chứng cổng chặn QC** | `python tdq_team.py open T1.1` -> `sweep` -> `python tdq_state.py set phase=qc` | **`0` / `0` / `2`** | Tạo nhánh `tdq/2026-11-13-1325-demo-calc/t1.1` và worktree `.tdq-worktrees\...\t1.1` (`1.1 MB`). Khi worktree đang mở, thử `set phase=qc` bị cổng `_chan_worktree_con_mo` **chặn cứng với `EXIT: 2`**: `1 worktree(s) still open: T1.1 ... Clean them up first`. |
| **4D. Kiểm tra, Merge & Dọn Worktree** | Commit `calc.subtract` trong worktree -> `tdq_team.py check T1.1` -> `merge T1.1` -> `sweep --clean` | **`0` / `0` / `0`** | `check T1.1` chạy `git merge-tree` sạch + chạy độc lập `pytest tests/test_calc.py` xanh (`EXIT: 0`). `merge T1.1` rebase lên `feat/demo-calc`, `merge --no-ff`, đóng sổ `worktrees.json` (`merged`), tự xóa thư mục worktree và xóa nhánh tạm. `sweep --clean` xác nhận `0 open`. |
| **6A. TDD Đỏ (`Red`) qua `tdq_test.py vung-cham`** | Thêm `test_format_diff` (chưa viết hàm) -> `python tdq_test.py vung-cham --files scripts/formatter.py tests/test_formatter.py --silent` | **`1`** | Bán kính ảnh hưởng chọn đúng `scope=direct` (`2 tests` trong `test_formatter.py`, không chạy thừa `test_calc.py`), trả về `[TDQ:TEST] FAIL — scope=direct backend=pytest tests=2 skipped=0 in 1.48s`. |
| **6B. TDD Xanh (`Green`) + Hermetic Receipt Reuse** | Viết `formatter.format_diff` + `docs/tdq/reuse-policy.json` -> chạy `vung-cham --reuse auto` **Lần 1** và **Lần 2** | **`0`** / **`0`** | **Lần 1:** `receipt action=executed reason=cache_miss` -> `PASS` (`1.80s`), lưu biên nhận vào `docs/tdq/cache/r-1584b3ebf4cce065/...`. **Lần 2 (không đổi mã):** `receipt action=reused reason=valid_terminal_receipt` -> **tái sử dụng ngay kết quả không cần chạy lại execution phase** (`1.32s`, chỉ chạy collection check)! |
| **6C. Chạy Full Suite (`tron-bo`) & Kiểm tra ngân sách (`so`)** | `python tdq_test.py tron-bo --silent` -> `python tdq_test.py so --json` | **`0`** / **`0`** | `[TDQ:TEST] PASS — scope=full backend=pytest tests=5 skipped=0 in 1.46s`, `bo_sot: 0`, `modules_bo_sot: []`. |
| **7A. Tick `[x]`, qua QC -> Report & thử đóng `idle` thiếu Archify** | Tick `[x]` toàn bộ `T1.1..T1.3`, viết `qc/<slug>.md` & `reports/<slug>.md` (đủ 4 mục bắt buộc) -> `set phase=report` -> thử `set phase=idle` | **`0`** -> **`1`** | Cổng `_chan_report_thieu` xác nhận đủ 4 mục báo cáo nhưng **chặn `set phase=idle` với `EXIT: 1`** vì báo cáo chưa render sơ đồ Archify (`Manifest not found: docs\tdq\reports\2026-11-13-1325-demo-calc.manifest.json`). |
| **7B. Render Archify Report & Khóa sổ bằng `tdq_finish.py`** | `tdq_archify.py render ... --out docs/tdq/reports/<slug>.html` -> `python tdq_finish.py --phase idle --files ... --log "..." --verbose` | **`0`** / **`0`** | Tất cả các bước hoàn tất sạch sẽ (`0 step(s) failed`): `khoa-token=skip · lint=ok (1 file) · worklog=ok · timing=ok (timing.jsonl written) · phase=ok (idle) · archify=skip · graphify=ok`. |

---

## 5. Phát Hiện 5 Lỗi Thực Tế (Bugs & Edge Cases) Trên Windows Khi Chạy E2E

Quá trình chạy E2E thực tế trên Windows đã phát lộ **5 lỗi kỹ thuật có thật** trong mã nguồn `scripts/` của `TDQ-Workflow` (kèm dòng mã chính xác):

1. **[P1 - Mâu thuẫn hợp đồng Schema] `tdq_harvest.py` sinh tệp tri thức bị chính `tdq_knowledge.py` từ chối (`EXIT: 1`):**
   - Tại `scripts/tdq_harvest.py:98-104` và `L175`, lệnh `tdq_harvest.py scan` / `approve` ghi YAML frontmatter bằng khóa tiếng Anh `status: candidate` / `status: approved`.
   - Ngược lại, `scripts/tdq_knowledge.py:22, 126-129` kiểm định hợp đồng O12 lại bắt buộc khóa tiếng Việt `trang_thai` thuộc `("candidate", "reviewed", "rejected", "superseded")`.
   - **Thực nghiệm E2E (Bước 7C):** Chạy `tdq_harvest.py scan` trích xuất thành công `k_20261113_133607_1.md` (`EXIT: 0`), nhưng chạy tiếp `tdq_knowledge.py check docs/tdq/knowledge/candidates` lập tức báo lỗi **`EXIT: 1`**:
     `tdq_knowledge: FAIL k_20261113_133607_1.md: Invalid or missing trang_thai: None (must be one of ('candidate', 'reviewed', 'rejected', 'superseded'))`.

2. **[P1 - Lỗi crash `NotADirectoryError` trên Windows] `tdq_team.py open` tạo nhánh trước khi tạo worktree; nếu `git worktree add` lỗi vì `MAX_PATH` 260 ký tự thì `tdq_team.py check` văng Traceback:**
   - Trên Windows, `git init` mặc định có `core.longpaths = false`. Khi dự án có `graphify-out/cache/ast/v0.9.64-s4/<64-hex>.json` được commit và mở worktree tại `.tdq-worktrees/<slug>/<task>/...`, tổng đường dẫn vượt quá 260 ký tự khiến `git worktree add` thất bại với mã `128` (`Filename too long`).
   - Tại `scripts/tdq_team.py:1112-1115`, nhánh `tdq/<slug>/<task>` đã được tạo ở dòng `1113` **trước** khi gọi `git worktree add` ở dòng `1115` và không được rollback khi dòng `1115` lỗi.
   - Sau đó khi gọi `tdq_team.py check T1.1`, `lenh_kiem` (`L1247`) chỉ kiểm tra nhánh tồn tại mà không kiểm tra thư mục worktree tồn tại, truyền `cwd=duong` không tồn tại vào `subprocess.run` (`L1211`), làm văng ngoại lệ chưa bắt `NotADirectoryError: [WinError 267] The directory name is invalid`!

3. **[P2 - Tương thích UTF-8 BOM của Windows PowerShell] `tdq_test.py` không đọc được tệp `.py` có UTF-8 BOM (`utf-8` thay vì `utf-8-sig`):**
   - Trên Windows PowerShell 5.1 (shell mặc định của `run_command` trên Windows!), `Set-Content -Encoding UTF8` luôn ghi 3 byte BOM (`EF BB BF`).
   - Trong khi `tdq_state.py:2045, 2453` và `tdq_transcript.py:149` đã cẩn thận dùng `encoding="utf-8-sig"`, thì `tdq_test.py:141` (`open(path, encoding="utf-8")`) giữ nguyên BOM khi đưa vào `ast.parse()`, gây lỗi `SyntaxError: invalid non-printable character U+FEFF`. Hệ quả: `tdq_test.py vung-cham` mất khả năng tính bán kính ảnh hưởng và ép chạy lại toàn bộ suite (`changed .py cannot be read or parsed`).

4. **[P2 - Cảnh báo giả `Stray state found`] `tdq_state.py` quét nhầm `docs/tdq/state.json` bên trong `.tdq-worktrees/`:**
   - Khi `docs/tdq/state.json` đã được theo dõi trong git và `tdq_team.py open` tạo cây thư mục `.tdq-worktrees/<slug>/<task>/`, hàm `find_shadow_states(cwd)` được gọi ở `tdq_state.py:2783` không loại trừ thư mục `.tdq-worktrees/`, phát cảnh báo giả trên mọi lệnh `tdq_state.py`:
     `⚠️ Stray state found: .tdq-worktrees\2026-11-13-1325-demo-calc\t1.1\docs\tdq\state.json`.

5. **[P3 - Bất nhất tài liệu / schema] Không có khóa `qc_file` trong `default_state()`:**
   - Trong khi `spec_file` và `plan_file` là khóa hợp lệ của `state.json`, việc gọi `tdq_state.py set qc_file=docs/tdq/qc/<slug>.md` bị từ chối với `EXIT: 2` (`Key does not exist in the schema: qc_file`). Đường dẫn tệp QC chỉ được suy diễn theo quy ước `docs/tdq/qc/<slug>.md`.

---

## 6. Kiến Nghị Khắc Phục Khi Chuyển Đổi Đầy Đủ Sang Antigravity Trên Windows

1. **Bổ sung đăng ký MCP `lsp` (`agent-lsp`) vào `build_portable.py --sinh-agy` và `tdq_setup.py`:** Thêm cấu hình `lsp` vào `mcp_config.json` của gói Antigravity (`~/.gemini/config/plugins/tdq-workflow/mcp_config.json`) và cập nhật tên công cụ trong `tdq_lsp.py kich-ban` theo định dạng `mcp_<plugin>_lsp_<tool>` của Antigravity để cổng `_cong_lsp` hoạt động tự nhiên không cần `--bo-qua-lsp`.
2. **Viết bộ đọc transcript Antigravity trong `tdq_transcript.py`, `step_audit.py` và `token_audit.py`:** Hỗ trợ đường dẫn `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (bỏ qua thư mục con `chunks/` và `transcript_full.jsonl` để tránh đếm nhân đôi), ánh xạ `PLANNER_RESPONSE` (`created_at`, `input_tokens`, `cache_read_tokens`, `output_tokens`, `tool_calls`) sang mô hình span và carry-cost của TDQ.
3. **Điều chỉnh `tdq-browser-research` & `tdq-browser-test` cho Antigravity:** Trên host Antigravity, ưu tiên ủy quyền cho subagent `browser` hoặc ánh xạ sang bộ công cụ `chrome-devtools-plugin` sẵn có (với tham số `pageId`), tránh gọi cứng tiền tố `mcp__chrome-devtools__*` của Claude Code.
4. **Vá 4 lỗi Windows/CLI nhỏ nhưng sát sườn:** Đồng bộ khóa frontmatter giữa `tdq_harvest.py` và `tdq_knowledge.py`; đổi `encoding="utf-8-sig"` trong `tdq_test.py:141`; tự bật `git config core.longpaths true` + rollback nhánh nếu `git worktree add` thất bại trong `tdq_team.py:1113-1115`; và thêm `.tdq-worktrees` vào danh sách loại trừ của `find_shadow_states()` trong `tdq_state.py`.
