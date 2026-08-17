# REPORT — portable_codex dùng lớp native của Codex (`2026-08-17-1139-codex-native-layers` · lane full · mode main · 18/18 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 trinh sát Codex CLI thật (`codex-cli 0.147.0-alpha.6.5`, bản trong ChatGPT.app) — chốt tên tool, khoá payload, cwd hook, hai cổng tin cậy · P2 `build_portable.py` sinh thêm ba lớp native cho `portable_codex/`: `.agents/skills/` (8 skill), `.codex/config.toml` (2 MCP server), `.codex/hooks.json` (4 event / 5 hook) + copy `hooks/` `scripts/` vào gốc bundle · P3 sinh `hooks/scripts/codex_edit_gate.py` bọc `edit_gate.py` để đọc đường dẫn từ patch của `apply_patch` · P4 `tdq_checkportable.py` thêm `setup --trust` ghi thật `[projects."<path>"] trust_level = "trusted"` vào `$CODEX_HOME/config.toml` kèm backup · P5 sửa README/AGENTS.md/SKILL.md/kien-truc.md cho khớp thực tế.

**Kết quả:** `portable_codex/` 24 → 121 file · skill Codex tự nạp 0 → 8 · MCP server 0 → 2 · hook 0 → 5 · test 728 → 764 pass (+36) · `portable_claude/` không đổi một byte (sha256 `1d34ce47…` trước/sau).

**Kiểm:** `python3 -m pytest tests/ -q` → `764 passed, 375 subtests passed in 43.29s` · `doc_lint` exit 0 trên spec/plan/qc · QC **PASS 11/11** hạng mục DoD (Q1–Q8, Q9a, Q10 + hồi quy), 0 defect, do agent `tdq-qc-tester` chạy lại độc lập; Q9a là vòng chạy Codex THẬT (`codex exec` với `CODEX_HOME` tạm) — skill được liệt kê, hook ghi đúng `.tdq-turn.jsonl`, `codex mcp list` thấy đủ 2 server.

**Đầu ra:** `scripts/build_portable.py` · `scripts/tdq_checkportable.py` · `portable_codex/` (sinh) · `docs/tdq/qc/2026-08-17-1139-codex-native-layers.md` · Backup ngoài repo: KHÔNG có — mọi lần thử `--trust` đều trỏ `CODEX_HOME` vào thư mục tạm, `~/.codex` thật xác nhận không đổi (sha256 + `find` diff rỗng).

**Lệch so với spec / quyết định:**
1. Quyết định A2 nói "dùng lại nguyên `hooks/scripts/*.py`, không viết adapter". Thực tế Codex gọi sửa file bằng tool `apply_patch` với `tool_input.command` là văn bản patch, **không có `file_path`** — `edit_gate.py` không có gì để đọc. Giải pháp: `edit_gate.py` trong repo giữ nguyên không sửa; chỉ SINH thêm `codex_edit_gate.py` (~40 dòng) vào bundle codex, nó rút đường dẫn từ patch rồi gọi lại `edit_gate.py`. Đã báo lệch này ngay lúc làm.
2. **Q9b không thực hiện được:** vòng người dùng bấm duyệt hook trong TUI Codex đòi phiên tương tác, phiên này headless. Đã ghi rõ trong file QC thay vì bỏ qua.
3. Hợp đồng `WebFetch` ở task T2.4 không cần dùng — đã lấy đủ sự thật bằng thăm dò chạy thật, chính xác hơn tài liệu.
4. Phát hiện ngoài spec, phải đổi tài liệu sản phẩm: Codex có **cổng tin cậy thứ hai** cho hook (trust hash duyệt trong giao diện) mà `--trust` không mở được → README/AGENTS.md/SKILL.md đổi từ "ba việc máy không tự làm được" thành **bốn**. User đã duyệt thay đổi này.

**Giới hạn:** Q9b chưa chạy (xem trên) · `tests/probe_codex_hook.py` là công cụ trinh sát để lại trong `tests/`, không phải test, không chạy trong suite · `sinh_mcp()` khai `TAVILY_API_KEY` trong khi máy này dùng `TAVILY_API_KEY_PRIMARY`/`_BACKUP` — lệch có sẵn từ trước, giống hệt `.mcp.json` hiện tại, không do request này gây ra và không sửa trong phạm vi này.

**Git:** CHƯA COMMIT gì. Không có commit gỡ chặn. Lưu ý: request trước `2026-08-17-0938-portable-codex` (sinh `build_portable.py` + `tdq_checkportable.py` + `portable_claude/` + xoá `portable/` cũ) cũng còn nguyên trong working tree chưa commit — hai request nằm chồng nhau trên cùng một chỗ làm việc.

## Bổ sung sau report (theo yêu cầu user lúc 14:27)

Viết hướng dẫn cài đặt vào README của CẢ HAI bundle (sửa ở `build_portable.py` rồi sinh lại,
không sửa tay file sinh): mục `## Cài ở máy mới` liệt kê từng bước theo đúng thứ tự
(claude 7 bước, codex 8 bước, nhấn "trust TRƯỚC, chạy SAU") · codex thêm mục `## Trust — ba
cách, chọn một` (script `setup --trust` · bấm trong Codex · sửa tay `config.toml`, kèm cảnh
báo đường dẫn phải tuyệt đối đã resolve symlink) · codex thêm mục giải thích vì sao bước kiểm
đầu tiên chạy thẳng file thay vì gọi skill (skill nằm trong bundle, chỉ được quét sau khi
trust + khởi động lại → vòng luẩn quẩn).

Lỗi bắt được trong lúc làm: bản nháp đầu ghi lệnh `python3 scripts/tdq_checkportable.py` cho
CẢ hai README, nhưng bundle claude đặt script ở `.claude/tdq/scripts/`. Đã sửa và khoá bằng
3 test mới (`TestHuongDanCaiDat`): mọi đường dẫn `python3 …py` nêu trong README phải là file
có thật trong chính bundle đó, và README codex phải còn đủ ba cách trust. Test: 764 → 767 pass.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 13 phút | 13 phút | 1 |
| spec | 21 phút | 3 phút | 1 |
| plan | 10 phút | 7 phút | 1 |
| implement | 1 giờ 42 phút | 41 phút | 1 |
| qc | 0 giây | 0 giây | 1 |
| report | 5 giây | 0 giây | 1 |
| **Tổng** | **2 giờ 27 phút** | **1 giờ 06 phút** | |
