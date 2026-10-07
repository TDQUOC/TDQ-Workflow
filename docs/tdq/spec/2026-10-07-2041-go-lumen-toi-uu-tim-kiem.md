# SPEC — Gỡ Lumen và tối ưu luật tìm kiếm 3 tầng

Ngày: 2026-10-07 · Bản: 1.0 · Brief: ../brief/2026-10-07-2041-go-lumen-toi-uu-tim-kiem.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi
- Mục tiêu: TDQ không còn phụ thuộc Lumen ở mã, luật, test, hook và trên máy user; luật tìm kiếm còn 3 tầng (LSP · grep · graphify) và search gate dẫn agent tới tầng đang sống, sao cho phiên thử của request `2026-10-07-1843` giảm lượt thừa từ 4 xuống ≤ 1; hook TDQ chạy thật trong Codex.
- Trong phạm vi:
  - Xoá mã lumen: bậc 5 và bộ dò binary/model/index (`tdq_lsp.py`), `wake`/`nha` ollama, bước `reindex` (`tdq_finish.py`), phần lumen của `tdq_setup.py` (cấu hình, smoke, dựng nền), `setup_status*.py`, `tdq_codex_mcp.py`, `session_start.py`; đánh số lại thang kiểm còn 7 bậc.
  - Luật chữ: `uu-tien-tim-kiem.md` (+ `-chi-tiet.md`), `analyze-full.md`, `quick-lane.md`, `tdq-build/SKILL.md`, `tdq-setup/SKILL.md`, `PHASE_TABLE` trong `tdq_state.py` (+ `phases.md` sinh lại), `plugin-routing.md`, `reminder-codes.md`; xoá `skills/tdq-setup/references/lumen.md`, `.lumenignore`.
  - Gate: lời nhắc khi chặn chỉ nêu tầng đang sống kèm lệnh dùng được; lời gọi LSP được ghi sổ ngay khi gọi (kể cả khi LSP trả "chưa khởi động").
  - Codex: tìm nguyên nhân hook TDQ không chạy và sửa; khối search gate trong `.codex/hooks.json` thành bản chính thức, 2 test cập nhật theo.
  - Test: xoá test chỉ phục vụ lumen, sửa test ghim chữ luật, thêm test cho hành vi gate mới.
  - Máy user (làm cuối, sau khi test xanh): gỡ plugin lumen; bỏ `[mcp_servers.lumen]` khỏi `~/.codex/config.toml`; bỏ env `OLLAMA_HOST`, `LUMEN_EMBED_MODEL` khỏi `~/.claude/settings.json`; xoá `~/.local/share/lumen`, `~/.config/lumen/`; `ollama rm qwen3-embedding:0.6b`; cập nhật khối luật trong `~/.claude/CLAUDE.md` qua `ghim_huong_dan_tool`.
  - Phát hành 0.58.0.
- NGOÀI phạm vi:
  - Đo lại chất lượng 12 câu (user không chọn 5C) · đo token skill (không chọn 5B) · hiệu năng máy.
  - Gỡ ollama và các model khác của ollama.
  - Sửa chính sách thực thi shell của Codex trên Windows (`blocked by policy`) nếu nó không cùng gốc với việc hook không chạy — khi đó chỉ ghi lại trong báo cáo.
  - `setup_status.py` lỗi khi thiếu `state.json`, `plugin-routing.md` dòng observability ngoài việc bỏ chữ lumen — để request khác.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (1 câu, tự làm) | cách codex-cli 0.155 nạp hook của dự án — chưa biết |
| Interview | CÓ | 2 vòng |
| spec → plan | CÓ | khung bất biến |
| QC độc lập (agent) | BỎ | mức `full` không đòi |
| Report + hỏi commit | CÓ | khung bất biến |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mã TDQ không còn lumen | `scripts/`, `hooks/` | không còn chữ `lumen` trong mã chạy (trừ chú thích lịch sử có lý do) |
| 2 | Luật tìm kiếm 3 tầng | `skills/**`, `scripts/tdq_state.py` | không câu luật nào đòi lumen; bảng loại câu hỏi → tầng chỉ có LSP/grep/graphify |
| 3 | Gate dẫn tới tầng sống | `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `hooks/hooks.json` | phiên thử lặp lại: lượt thừa ≤ 1 |
| 4 | Hook TDQ chạy trong Codex | `.codex/hooks.json`, mã liên quan | phiên Codex thử ghi được dòng vào sổ tìm kiếm |
| 5 | Test khớp hệ mới | `tests/` | trọn suite: 0 module đỏ |
| 6 | Máy user sạch lumen | ngoài repo | không còn plugin, MCP Codex, env, dữ liệu, model lumen; bản sao cấu hình trước khi sửa |
| 7 | Phát hành 0.58.0 | `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | 2 file cùng `0.58.0`, CHANGELOG có mục 0.58.0 |

## 2b. Ranh giới module

Mỗi module gồm cả test của chính nó (danh sách file test nằm ở plan). Ranh giới lấy theo ai gọi ai (bộ dò lumen sống ở `tdq_lsp.py` và được `tdq_setup`, `tdq_finish`, `tdq_codex_mcp`, `setup_status` import — đo bằng grep tên chính xác trên `scripts/ hooks/ tests/`).

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| thang-kiem | `scripts/tdq_lsp.py`, `scripts/tdq_setup.py`, `scripts/tdq_finish.py`, `scripts/setup_status.py`, `scripts/setup_status_render.py`, `hooks/scripts/session_start.py` | không | 1, 5 |
| gate | `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `hooks/scripts/search_observe.py`, `hooks/hooks.json` | thang-kiem (dấu mốc sẵn sàng còn 3 tầng) | 3, 5 |
| codex | `scripts/tdq_codex_mcp.py`, `.codex/hooks.json` | gate | 4, 5 |
| luat-chu | `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md`, `skills/tdq-setup/references/lumen.md`, `skills/tdq-setup/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/references/*.md`, `scripts/tdq_state.py` | thang-kiem (số bậc) | 2, 5 |
| phat-hanh | `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.lumenignore`, `.gitignore` | mọi module trên | 1, 7 |
| may-user | ngoài repo: `~/.claude/settings.json`, `~/.codex/config.toml`, `~/.claude/CLAUDE.md`, `~/.local/share/lumen`, `~/.config/lumen`, ollama | mọi module trên | 6 |

## 3. Cách tiếp cận & lý do
- Chọn:
  1. **Xoá trước, viết luật sau**: gỡ mã lumen theo module (thang-kiem → gate → codex), mỗi bước chạy test vùng chạm; luật chữ viết lại khi mã đã ổn để số bậc và tên lệnh trong luật khớp mã thật.
  2. **Luật 3 tầng**: giữ cách chọn theo LOẠI câu hỏi. Hàng "khái niệm mơ hồ" chuyển sang: graphify `query` (hiểu câu tự nhiên trên đồ thị) song song grep nhiều từ đồng nghĩa — dựa trên số đo request trước (không lumen vẫn 11–12/12 trúng).
  3. **Gate**: (a) lời nhắc khi chặn sinh từ dấu mốc sẵn sàng, chỉ liệt kê tầng `san_sang`, mỗi tầng một lệnh dùng ngay (`mcp__lsp__start_lsp` rồi `find_symbol`; `graphify query "<câu hỏi>"`); (b) ghi sổ lời gọi `mcp__lsp__*` ở PreToolUse như Codex đã làm, để lời gọi lỗi vẫn tính; (c) giữ nguyên ba luật chặn hiện có.
  4. **Codex**: thử hook tối giản (ghi một dòng ra file) trong `codex exec` để tách "hook không nạp" khỏi "lệnh python của hook bị chính sách chặn"; sửa theo nguyên nhân tìm được.
  5. **Máy user làm cuối**, mỗi file cấu hình có bản sao `*.truoc-tdq-<thời điểm>.bak` theo lệ của `tdq_setup`; dữ liệu xoá (index, model) là không hoàn tác — đã được user chọn (2B, 2C).
- Vì: số đo request trước cho thấy lumen không đem lại khác biệt đáng kể mà tốn mã, token và lượt thừa; luật chữ gãy là thứ duy nhất làm hỏng workflow khi thiếu lumen.
- Đã loại:
  - Giữ lumen làm tầng tuỳ chọn — user chọn xoá hẳn (1A).
  - Gate chỉ nhắc / bỏ gate — user chọn giữ chặn (3A).
  - Giữ số bậc cũ để lỗ ở bậc 5 — để lại số lạ trong mọi chỗ trích "bậc N".

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | project | NỀN | khung workflow đang chạy |
| tdq-setup | project | DÙNG | nguồn luật 4 tầng cần viết lại, `ghim_huong_dan_tool` cập nhật CLAUDE.md |
| Đã xét 18 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: giữ log sẵn có của các script/hook bị sửa (timestamp, tắt bằng `TDQ_LOG=0`); dòng log mới cho hành vi mới của gate (lời nhắc sinh từ tầng sống) và của phần sửa hook Codex.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi hành vi mới (lời nhắc theo tầng sống, ghi sổ LSP ở PreToolUse, thang 7 bậc, hook Codex) có unit test riêng, chạy bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (`docs/kien-truc.md`):
- "`hooks/scripts/search_gate.py` trả `deny` (mã `TDQ:SEARCH`) cho một lần tìm code đi tắt tầng khái niệm … Cổng phải chặn chứ không nhắc" — việc này chạm ở `search_gate.py`, `search_rules.py`: giữ chặn, chỉ đổi lời nhắc và cách ghi sổ.
- Hub `Changelog`, `main()` — sửa `CHANGELOG.md` và `main()` của `tdq_lsp.py`/`tdq_setup.py` phải khai ở dòng `Chạm:` và có dòng DoD hồi quy.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Xoá index/model là không hoàn tác | muốn dùng lại lumen phải index lại từ đầu, kéo lại model 639 MB | user đã chọn (2B, 2C); làm cuối cùng, sau khi test xanh và đo xong |
| Gỡ plugin lumen giữa phiên đang chạy | MCP lumen của phiên này chết | làm ở bước cuối; mọi bước sau không cần lumen |
| Đánh số lại thang kiểm làm lệch chỗ trích "bậc N" | tài liệu/test nói sai bậc | grep "bậc [5-8]" trên `scripts/ hooks/ skills/ tests/` sau khi đổi |
| Nguyên nhân hook Codex không sửa được trong repo (do Codex/Windows) | Đầu ra 4 không đạt | áp cột dự phòng Q5, ghi `lech add`, báo cáo nêu rõ nguyên nhân |
| Phiên thử Claude Code dao động theo model | lượt thừa đo ±1 | chạy 2 lần, lấy lần xấu hơn |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Mã không còn lumen | trong `scripts/`, `hooks/` không còn tham chiếu chạy được tới lumen; mỗi chữ `lumen` còn lại là chú thích lịch sử có lý do | 2026-10-07: 9 file trong `scripts/` + 4 file trong `hooks/` nhắc lumen | — |
| Q2 | Luật 3 tầng | không câu luật nào trong `skills/` và `PHASE_TABLE` đòi gọi lumen; bảng loại câu hỏi chỉ còn LSP/grep/graphify | 2026-10-07: 4 câu chấm oan + bảng 4 tầng | — |
| Q3 | Thang kiểm 7 bậc | `tdq_lsp.py check` in 7 bậc đánh số liền, smoke 3 tầng; trên máy này dòng tổng ĐẠT, exit 0 | 2026-10-07: 8 bậc, CHƯA ĐẠT, exit 4 (khi vắng lumen) | — |
| Q4 | Gate bớt lượt thừa | lặp lại phiên thử Claude Code của request trước (cùng câu hỏi, bản sao repo, 2 lần): lượt thừa trước khi grep chạy được ≤ 1 ở lần xấu hơn; lời nhắc không nhắc lumen | đo 2026-10-07: 4 lượt thừa (2 chặn, 1 `ToolSearch("lumen")`, 1 LSP chưa khởi động) | còn 2 lượt → ghi `lech add`, giữ bản sửa nếu đã giảm so với 4 |
| Q5 | Hook TDQ chạy trong Codex | một phiên `codex exec` trên bản sao repo ghi ít nhất 1 dòng của phiên đó vào sổ tìm kiếm | đo 2026-10-07: 0 dòng | nguyên nhân nằm ngoài repo (Codex/Windows) → ghi `lech add` kèm bằng chứng nguyên nhân và cách user tự bật |
| Q6 | Test | trọn suite 0 module đỏ | mốc 2026-10-07: 3 module đỏ (2 do `.codex/hooks.json`, 1 test reindex phụ thuộc ollama) | — |
| Q7 | Hồi quy hub | `CHANGELOG.md` mục mới không làm vỡ mục cũ; `main()` của `tdq_lsp.py` và `tdq_setup.py` chạy hết đường chính | — | — |
| Q8 | Máy user sạch lumen | không còn: plugin lumen trong `enabledPlugins`/cache, `[mcp_servers.lumen]`, env `OLLAMA_HOST`/`LUMEN_EMBED_MODEL`, `~/.local/share/lumen`, `~/.config/lumen`, model `qwen3-embedding:0.6b`; có bản sao của 2 file cấu hình; khối luật trong `~/.claude/CLAUDE.md` là bản 3 tầng | — | — |
| Q9 | Phát hành | 2 `plugin.json` cùng `0.58.0`, CHANGELOG có mục 0.58.0 | 0.57.0 | — |

DoD: Q1–Q9 PASS (hoặc PASS có lệch đã ghi); report có bảng trước/sau của Q3, Q4, Q5.

## 7. Câu hỏi còn mở
