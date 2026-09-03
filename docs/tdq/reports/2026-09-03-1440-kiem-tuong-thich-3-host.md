# REPORT — Sửa tương thích 3 host (`2026-09-03-1440-kiem-tuong-thich-3-host` · lane full · mode main · 15 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 dựng lại bundle agy đúng chuẩn plugin agy 1.1.11 (`plugin.json` ở gốc, `hooks.json`
+ `mcp_config.json` ở gốc, bỏ `config/`, bỏ hẳn `settings.json`, README 3 bước thật) · P2 hook agy
dùng đường dẫn tuyệt đối đã bung `~` và payload deny mang cả `allow_tool: false` lẫn
`decision: "deny"` · P3 README codex thêm mục trust hook theo `trusted_hash` và mục
`export TAVILY_API_KEY` · P4 `plugin.json` Claude thêm `displayName` + `userConfig` 2 khoá Tavily
(`sensitive: true`), marketplace bỏ chữ "Local" · P5 `tdq_checkportable.py` nhận diện layout mới,
thêm `tests/test_tuong_thich_host.py`.

**Kết quả:** đường cài agy 6 đường đoán → 1 đường thật · file ghi đè nguy hiểm 1 → 0 ·
`agy plugin validate` trên bundle: chưa chạy được → `[ok]` 9 skills / 2 mcpServers / 2 hooks ·
test 1471 xanh → 1478 xanh, đỏ giữ nguyên mốc 100.

**Kiểm:** `pytest -q` 100 failed / 1478 passed (mốc đỏ cũ 100, không tăng) ·
`pytest tests/test_tuong_thich_host.py -q` 6 passed · `claude plugin validate .` exit 0 ·
`tdq_checkportable check` CLEAN 85/142/92 · `doc_lint.py` exit 0 · QC PASS 15/15 hạng mục
(11 dòng DoD + 4 mục cố định), 1 defect tự phát hiện và sửa trong QC.

**Đầu ra:** `docs/tdq/qc/2026-09-03-1440-kiem-tuong-thich-3-host.md` ·
`scripts/build_portable.py` · `scripts/tdq_checkportable.py` · `hooks/scripts/agy_*.py` ·
`.claude-plugin/{plugin,marketplace}.json` · 3 thư mục bundle dựng lại. Backup: không sửa gì
ngoài repo nên không có backup.

**Giới hạn:** (1) `hooks.json` agy mang đường dẫn tuyệt đối bung ở lúc DỰNG, nên bản commit trong
repo giữ `$HOME` của máy dựng — người dùng khác phải tự dựng lại; `check` in NOTE khi lệch, README
nói rõ. (2) Layout agy đọc từ MỘT máy `agy 1.1.11`. (3) `agy plugin list` không dùng làm cổng kiểm
được vì nó chỉ liệt kê plugin đã import, mà cài thật thì phải ghi vào `~/.gemini` — spec §5 cấm;
đã đổi sang `agy plugin validate`, là lệnh ĐỌC và bằng chứng mạnh hơn. (4) Key Tavily lộ trong lịch
sử git vẫn chưa xoay — ngoài phạm vi yêu cầu này.

**Git:** chưa commit — không tạo commit nào trong lượt này.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 5 min | 5 min | 1 |
| spec | 12 min | 9 min | 1 |
| implement | 16 min | 15 min | 1 |
| qc | 1 min | 1 min | 1 |
| report | 6s | 5s | 1 |
| **Total** | **34 min** | **34 min** | |
