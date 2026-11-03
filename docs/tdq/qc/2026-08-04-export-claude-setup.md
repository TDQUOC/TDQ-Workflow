# QC — export-claude-setup (2026-08-04)

Đối chiếu Definition of Done (spec §6 / plan). Mỗi dòng: PASS/FAIL + bằng chứng.

- **Q1** (T1.1) — PASS. `claude-export/INSTRUCTIONS.md` có đủ 7 bước (thu thập trạng
  thái → lọc secret/runtime → copy file local + repo → rewrite path tdq-local →
  điền manifest → điền README → ghi log), mỗi bước có lệnh cụ thể. Ghi chú lệch câu
  chữ spec §6/Q1 cũ ("6 bước") đã note ngay dưới T1.1 trong plan — không phải lỗi.

- **Q2** (T1.2) — PASS. `python3 -c "import json; json.load(open('claude-export/MANIFEST.template.json'))"`
  → exit 0. 5 khoá bậc 1: `plugins`, `marketplaces`, `mcp_servers`, `cli_dependencies`, `excluded`.

- **Q3** (T1.3, T3.2) — PASS. `README.template.md` đủ 6 mục theo thứ tự. Bản điền
  thật `README.md`: `grep -c "^- \`.*@claude-plugins-official\`$\|^- \`.*@tdq-local\`$"`
  → 49, khớp 100% `manifest.json` (Q6).

- **Q4** (T2.4, T4.3) — PASS. `grep -rEi "sk-|api[_-]?key|token" claude-export/ --include="*.json" --include="*.md"`
  chỉ khớp tên biến placeholder (`TAVILY_API_KEY_PRIMARY`/`BACKUP`), không có giá trị
  thật. Đối chiếu thêm trên bundle thật (`~/Documents/claude-code-export/`): đếm số
  dòng trùng khớp 2 giá trị key thật (giữ trong biến shell tạm, không in ra) → 0.

- **Q5** (T2.4/T2.5/T3.1/T3.2) — PASS. `ls ~/Documents/claude-code-export/` →
  `README.md config manifest.json tdqworkflow-repo`; `ls .../config/` → 9 mục đúng
  danh sách Bước 3 của INSTRUCTIONS.md.

- **Q6** (T3.1) — PASS. So sánh bằng Python: danh sách plugin scope=`user` từ
  `installed_plugins.json` nguồn (49) và `manifest.json` bundle (49) — sort rồi so
  `==` → `True`.

- **Q7** (T3.3) — PASS. `tail claude-export/EXPORT_LOG.md` có 2 dòng
  `2026-08-04 14:13`/`14:16` đúng định dạng `YYYY-MM-DD HH:MM — <tóm tắt>`.

- **Q8** (T2.6) — PASS. Path `tdq-local` trong `config/settings.json`
  (`extraKnownMarketplaces.tdq-local.source.path`), `config/known_marketplaces.json`
  (`tdq-local.source.path` và `tdq-local.installLocation`) — cả 3 giá trị giống hệt
  `/Users/truongdinhquoc/Documents/claude-code-export/tdqworkflow-repo`.

- **Q9** (T3.4) — PASS. Test `TDQ_EXPORT_NO_LOG=1` trước khi chạy Bước 7: md5 +
  số dòng `EXPORT_LOG.md` giống hệt trước/sau — guard chặn đúng cả 2 lệnh ghi log.

- **Q10** (T4.2) — PASS (sau 1 vòng fix). Sweep lần đầu phát hiện 6 mục lọt vào
  `tdqworkflow-repo/` do rsync T2.5 chỉ `--exclude='.git'`: 1 file `*.bak*`
  (`docs/tdq/qc/claude-md-backup-2026-08-02.bak`), 4 thư mục `__pycache__`, 1 thư
  mục `.remember/logs/`, 1 thư mục `graphify-out/cache/` — tất cả untracked/
  regenerate-được. Đã xoá khỏi bundle đã sinh + thêm 4 `--exclude` vào rsync của
  `INSTRUCTIONS.md` Bước 3 (quyết định ghi ở working log 14:24). Sweep lại toàn bộ
  18 pattern loại trừ §1 trên bundle → rỗng.

## Kết luận
10/10 hạng mục PASS. Không còn task fix nào cần thêm vào plan.
