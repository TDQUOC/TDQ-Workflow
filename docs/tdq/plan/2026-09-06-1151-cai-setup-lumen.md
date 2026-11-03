# Mini-plan — 2026-09-06-1151-cai-setup-lumen
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
Cài lumen mức **user**: binary trần + config 2 endpoint + MCP scope user + model ở local. **Không** cài plugin
`lumen@claude-plugins-official` (hook `PreToolUse` phá bậc 6 — brief §xung đột 2). **Không** sửa `tdq_lsp.py`
(bậc 5 vẫn cảnh báo, chấp nhận có chủ đích). Branch: ở nguyên `chore/cai-uv-pyenv-graphify`.

## Task
- [x] **T1 — Binary.** Tải `lumen-0.0.42-darwin-arm64` từ GitHub release → `~/.local/bin/lumen`, `chmod +x`.
      Không sudo, không đụng `/usr/local/bin`. Test: `command -v lumen` ra đúng `~/.local/bin/lumen`.
- [x] **T2 — Config 2 endpoint.** Tạo `~/.config/lumen/config.yaml` (backup nếu đã có):
      `servers:` list 2 phần tử, **thứ tự = ưu tiên** — [0] `backend: ollama, host: http://100.122.225.62:11434`,
      [1] `backend: ollama, host: http://localhost:11434`; cả hai `model: qwen3-embedding:0.6b`.
      Không set `dims`/`ctx_length`/`min_score` (`models.go:67` đã có 1024/32768/0.30). Test: parse YAML đúng 2 server, đúng thứ tự.
- [x] **T3 — Ollama local + pull model.** Bật daemon local (`ollama serve` nền), chờ cổng 11434 mở,
      rồi `ollama pull qwen3-embedding:0.6b` (**0.64 GB** — đo từ primary; đĩa còn 401 Gi, RAM 24 GB).
      Test: `ollama list` có model + manifest tồn tại dưới `~/.ollama/models/manifests/`.
- [x] **T4 — Đăng ký MCP.** `claude mcp add --scope user lumen -- ~/.local/bin/lumen stdio`.
      Test: `claude mcp list` báo Connected + key **gốc** `mcpServers` của `~/.claude.json` có `lumen`
      (không rơi vào `projects[<cwd>]` — bài học request LSP trước).
- [x] **T5 — Nghiệm thu failover thật.** Đo cả 2 nhánh, không suy luận:
      (a) primary sống → embed đi về `100.122.225.62`; (b) chặn primary bằng config tạm → rơi xuống `localhost`,
      vẫn ra vector. Khôi phục config gốc sau khi đo.
- [x] **T5b — Đo tiếng Việt (thêm sau câu hỏi của bạn).** lumen có nhét comment dẫn đầu vào chunk
      (`goast.go:39` `parser.ParseComments`; `treesitter.go:113-116` `findLeadingComments`, tối đa 10 dòng)
      và index cả `.md/.mdx` → comment tiếng Việt **có** được embed. Đo: index thư mục thử có hàm kèm comment
      tiếng Việt, truy vấn tiếng Việt xem hàm đó có trong top-k, đối chiếu cùng truy vấn bằng tiếng Anh.
      Số đo vào QC; tiếng Việt trượt thì tôi báo bạn chọn model khác, không tự đổi.
- [x] **T6 — Chạy lại thang.** `python3 scripts/tdq_lsp.py check`, ghi lại số bậc đạt trước/sau vào mục QC.

## Definition of Done
1. `lumen version` (không phải `--version`, flag đó không tồn tại) chạy từ `~/.local/bin/lumen`; chỉ ghi trong `~/.local/bin`, `~/.config/lumen`, `~/.ollama`, `~/.claude.json`; không sudo.
2. `~/.config/lumen/config.yaml` parse hợp lệ, đúng 2 server đúng thứ tự primary→backup, model `qwen3-embedding:0.6b`.
3. Model có ở **local**; primary đã sẵn (đo ở brief B1). MCP `lumen` scope user, `claude mcp list` Connected.
4. Failover chứng minh bằng đo thật cả hai nhánh (T5); truy vấn tiếng Việt có số đo (T5b) — không kết luận bằng lời.
5. Bậc 6 **không tụt**; bậc 5 **được phép cảnh báo** vì `MODEL_LUMEN` hardcode jina — ghi rõ trong QC, không lặng lẽ sửa DoD.
6. Turn có thay đổi repo → append working log; không commit gì nếu bạn không yêu cầu.

## Rủi ro
- Tool `mcp__lumen__*` chỉ nạp sau **restart Claude Code** (như `mcp__lsp__*` lần trước) → T5/T5b có thể phải đo bằng
  binary trực tiếp; sẽ nói rõ đo bằng đường nào.
- **`qwen3-embedding:0.6b` bị upstream đánh dấu *Untested*** — chạy được, dims 1024/ctx 32768, nhưng chất lượng
  search họ chưa đo → đó là việc của **T5b**. Nếu T5b kém, lối nâng là `:8b` (*Best quality*, 4.68 GB, đổi lại
  "very slow indexing"), **không phải `:4b`** (upstream ghi *Not recommended*).
- **Không có chỗ nào để gắn "model truy xuất".** Config chỉ có 6 trường và đúng 1 `model` (`service.go:24-29`);
  lumen chỉ gọi `/api/tags` + `/api/embed` của Ollama. Vì vậy plan KHÔNG cấu hình model sinh nào.
- **Hai endpoint bắt buộc dùng CÙNG model** (dims khác nhau → vector không khớp index, `models.go:65-67`).
  Đổi model sau này phải **index lại toàn bộ**, không chỉ sửa config.

## QC — 2026-09-06 12:24

| # | Kiểm | Kết quả |
|---|---|---|
| Q1 | `lumen version` từ `~/.local/bin/lumen` | **PASS** — `0.0.42`, 34.2 MB, `-rwxr-xr-x tdq`. `/usr/local/bin/lumen` không tồn tại, không sudo |
| Q2 | Config 2 server đúng thứ tự | **PASS** — [0] `100.122.225.62:11434`, [1] `localhost:11434`, cả hai `ollama` + `qwen3-embedding:0.6b` |
| Q3 | Model ở local | **PASS** — `ollama list`: `qwen3-embedding:0.6b` 639 MB; manifest `~/.ollama/models/manifests/registry.ollama.ai/library/qwen3-embedding/0.6b` |
| Q4 | MCP scope user | **PASS** — root `mcpServers` = `[tavily-primary, tavily-backup, lsp, lumen]`; `projects[repo].mcpServers` = `[]`; `claude mcp list` → `lumen … ✔ Connected` |
| Q5 | Failover nhánh (a) primary sống | **PASS** — log: `selected embedding server server=0 host=http://100.122.225.62:11434` |
| Q6 | Failover nhánh (b) primary chết | **PASS** — log: `health probe failed server=0` → `selected embedding server server=1 host=http://localhost:11434`; search **vẫn ra kết quả đúng** (`zz_one` score **0.77**, y hệt điểm khi chạy primary → hai endpoint sinh vector giống nhau). Config đã khôi phục, `diff` == bản gốc, lần chạy sau quay lại server 0 |
| Q7 | Comment tiếng Việt (T5b) | **PASS 7/7 top-1** — xem bảng dưới |
| Q8 | Bậc 6 không tụt | **PASS** — trước và sau đều ĐẠT ("không plugin nào chèn thứ tự tìm kiếm khác"). Đây là kết quả của việc cố ý bỏ đường cài plugin |
| Q9 | Thang 7 bậc | **6/7 ĐẠT · 0 bậc thiếu · 1 cảnh báo** — đúng như DoD#5 dự liệu |
| Q10 | Bậc 5 | **CẢNH BÁO có chủ đích** — `tdq_lsp.py:42` hardcode `ordis/jina-embeddings-v2-base-code`, không phải model ta cấu hình. Không chặn gì (`chi_canh_bao=True`). Chưa sửa vì nằm ngoài phạm vi |

### Q7 chi tiết — phép đo tiếng Việt

Bộ thử: 7 hàm tên **cố ý vô nghĩa** (`proc_a`…`proc_e`, `zz_one`, `zz_two`) — ngữ nghĩa **chỉ** nằm ở
comment tiếng Việt. Nếu tên hàm mang nghĩa thì phép đo vô giá trị, nên phải làm vậy.

| Truy vấn | Đích | Top-1 | Score |
|---|---|---|---|
| "tính thuế thu nhập cá nhân" | `proc_a` | chunk chứa `proc_a` | 0.58 |
| "gửi email xác nhận cho khách hàng" | `proc_b` | `proc_b` | 0.72 |
| "nén ảnh cho nhẹ bớt" | `proc_c` | `proc_c` | 0.56 |
| "kết nối cơ sở dữ liệu có thử lại" | `proc_d` | chunk chứa `proc_d` | 0.66 |
| "dọn dẹp file tạm cũ" | `proc_e` | `proc_e` | 0.58 |
| "xác minh chữ ký số của file tải về" | `zz_one` | `zz_one` | **0.77** |
| "quy đổi ngoại tệ sang tiền đồng" | `zz_two` | `zz_two` | 0.62 |

**Đối chứng chéo ngôn ngữ** (truy vấn tiếng Anh, comment vẫn tiếng Việt): "verify digital signature of
downloaded file" → `zz_one` **0.79**; "calculate personal income tax" → chunk chứa `proc_a` **0.62**.
Tiếng Anh còn nhỉnh hơn tiếng Việt một chút, nghĩa là model thật sự đa ngữ chứ không phải khớp chuỗi.

Cũng đã thử comment **không dấu** (`proc_a`…`proc_e`) lẫn **có dấu đầy đủ** (`zz_one`, `zz_two`) — cả hai
đều trúng. Kết luận: `qwen3-embedding:0.6b` xử lý comment tiếng Việt **tốt**, không cần nâng lên `:8b`.

### Sai lệch so với DoD — báo cáo thẳng

- **DoD#1 nói chỉ ghi trong 4 nơi, thực tế có nơi thứ 5**: `~/.local/share/lumen/` (index SQLite +
  `debug.log`). Đây là chỗ lumen bắt buộc phải ghi khi index — mà T5/T5b thì bắt buộc phải index mới đo
  được. DoD của tôi viết thiếu, không phải lumen ghi bậy. Dọn sau bằng `lumen clean`.
- **DoD#1 ghi `lumen --version`; flag đó không tồn tại**, lệnh đúng là `lumen version`. Đã sửa trong DoD.
