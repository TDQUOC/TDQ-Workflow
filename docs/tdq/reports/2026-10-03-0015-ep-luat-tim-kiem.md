# REPORT — Ép luật tìm kiếm 4 tầng cho Claude Code và Codex (`2026-10-03-0015-ep-luat-tim-kiem` · lane full · mode subagent · 33/35 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** cổng tìm kiếm `PreToolUse` (`hooks/scripts/search_gate.py`, mã `TDQ:SEARCH`) **chặn**
lần tìm code đi tắt tầng khái niệm theo ba luật: (1) miễn lọc danh sách file và tên có nguyên văn
trong prompt; (2) request chưa hỏi lumen/LSP/graphify → chặn; (3) một lần hỏi mở khoá 10 lần tìm,
sau đó grep kiểu đoán mò (`a\|b\|c`) bị chặn lại · luật thuần dùng chung ở `scripts/search_rules.py`
(cổng và bộ phát lại chạy CÙNG một luật) · sổ riêng sống qua lượt (`search_observe.py`) · Codex có
cùng cổng qua `.codex/hooks.json` cấp project + MCP lumen/LSP khai qua `codex mcp add` (chỉ thêm, có
backup) · bậc 3 khởi động language server thật, smoke grep theo ngôn ngữ thật, thang + smoke một
lệnh · đường dẫn tuyệt đối trong output hook · `SessionStart` tự dựng bộ tìm kiếm ở nền (tách rời,
khoá pid) và cổng đứng xuống — nói ra — khi tầng khái niệm chưa có · quyết định kiến trúc ghi ở
`docs/kien-truc.md`.

**Kết quả:** phát lại phiên excalidraw thật: **bắt 11 · bắt oan 0 · lọt 0**, lượt 7 (`fileHandle`)
và lượt 9 (`^export`) đều bị bắt. Hai reviewer độc lập tìm **18 phát hiện, nhận cả 18**, sửa qua
F1–F9 — trong đó có lỗ thật: `bash -c '…'`/`powershell -Command` lọt cổng, `echo graphify query`
mở khoá giả, request đã đóng vẫn mở khoá cho việc sau, cập nhật plugin nhân đôi hook Codex.

**Kiểm:** trọn bộ `python -m unittest discover tests` → `Ran 2336 tests · OK (skipped=9)` trên
Windows 3.13 · QC **21/23 PASS** · `doc_lint skills` exit 0 · `token_budget --kiem` exit 0 ·
`i18n_check` 5 file mới → 0 dòng Việt. QC: `docs/tdq/qc/2026-10-03-0015-ep-luat-tim-kiem.md`.

**Đầu ra:** `scripts/search_rules.py` · `scripts/search_replay.py` · `scripts/tdq_codex_mcp.py` ·
`hooks/scripts/search_gate.py` · `hooks/scripts/search_observe.py` · sửa `tdq_setup.py`,
`tdq_lsp.py`, `tdq_state.py`, `session_start.py`, `prompt_context.py`, `_common.py`, `hooks.json`
(10 hook / 6 event) · fixture `tests/fixtures/phien_excalidraw_tim.json` · 12 file test mới.
Ngoài repo: `~/.codex/config.toml` có thêm `lumen` + `lsp` (backup cạnh nó, `cloudcli-browser`
còn nguyên); `typescript@5.9.3` cài lại global vì `typescript@7` không có `tsserver`.

**Giới hạn:**
- **Q9 — Codex bị chặn trong một lượt thật: chưa chạy được.** Codex chưa đăng nhập (`codex login
  status` → `Not logged in`). Khuôn `deny` đã khoá bằng 13 test.
- **Q19 / T8.4 — macOS và Linux chưa chạy.** Cả hai máy không trả lời ping (kiểm lại hôm nay).
- **N = 10 chốt bằng lý lẽ, không phải số đo** — fixture không phân biệt được N = 5…20.
- **Máy excalidraw đang dùng bản plugin cũ** cho tới khi `claude plugin marketplace update
  tdq-local` rồi cập nhật plugin.

**Git:** nhánh `feature/ep-luat-tim-kiem`, 46 commit trên `main`, chưa merge. Commit làm việc của
team mode (mỗi nhánh con gộp vào nhánh request) cùng **8 commit sổ sách để mở khoá merge** — lệnh
merge từ chối khi file theo dõi còn bẩn: `adbffe0`, `45947dc`, `b5069cf`, `ad62894`, `4dd184c`,
`5b8d806`, `d44eabc`, `1339048`. Bảy commit cuối từng mang trailer AI trái luật bước 10 — đã gỡ
bằng `git filter-branch --msg-filter` trên nhánh local (chưa push, cây file không đổi). Bản plugin
bump **0.54.0 → 0.55.0** kèm mục CHANGELOG.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 5 min | — | 1 |
| spec | 38 min | — | 1 |
| plan | 1h 39min | — | 1 |
| qc | 41s | — | 1 |
| report | 0s | — | 1 |
| **Total** | **2h 23min** | **—** | |

Nguyên văn từ `tdq_timing.py show`. Bảng không có dòng `implement`: phần làm của team mode chạy
khi state vẫn ghi `plan`→`implement` mà bộ đếm không bắt được lần vào `implement`, nên thời gian đó
nằm lẫn trong các dòng trên — không ước lượng bù. Cột `Model time` là `—` vì `tdq_timing.py` dò
thư mục transcript theo đường POSIX, không đọc được phiên Windows (nợ đã khai ở request trước).
