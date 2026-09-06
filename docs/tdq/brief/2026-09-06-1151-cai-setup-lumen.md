# 2026-09-06-1151-cai-setup-lumen
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hãy giúpt ôi mở request nhanh để install và setup lumen cho máy này để embeding là
> qwen3-embeding:0.6b và tríct xuất dùng model mặc định. set 2 endpoint primary sẽ về ip
> 100.122.225.62 và backup sẽ về local hãy setup và pull model giúp tôi luôn đi

**Đọc lần đầu.** Mục tiêu: máy này có lumen chạy được, embedding bằng
`qwen3-embedding:0.6b`, hai endpoint Ollama theo thứ tự ưu tiên — primary
`http://100.122.225.62:11434`, backup `http://localhost:11434` — và model được pull sẵn.

Phạm vi đoán: cài binary lumen + `~/.config/lumen/config.yaml` + đăng ký MCP scope user +
bật ollama local + pull model về local. Không đụng repo code trừ chỗ nêu ở mục xung đột.

Chỗ chưa rõ (giải quyết bằng giả định nêu rõ, không đoán ngầm):
"trích xuất dùng model mặc định" — lumen **không dùng LLM để trích xuất**, phần trích xuất là
AST parsing thuần Go. Nên hiểu là: giữ nguyên mọi mặc định còn lại
(`LUMEN_MAX_CHUNK_TOKENS=512`, `LUMEN_VECTOR_STORAGE=int8`, không set `LUMEN_EMBED_DIMS`),
chỉ đổi đúng model embedding. Nếu ý bạn khác thì nói, tôi sửa plan.

## Hiểu & kiến thức

### B1 — Hiện trạng máy (đo thật)

| Mục | Kết quả |
|---|---|
| Endpoint primary `100.122.225.62:11434` | **SỐNG** (Ollama qua Tailscale; máy này = `100.105.75.71`) |
| Model trên primary | đã có `qwen3-embedding:0.6b` (0.64 GB), `:4b`, `:8b`, `ordis/jina-embeddings-v2-base-code`, `embeddinggemma`, … |
| ollama local | binary `/opt/homebrew/bin/ollama` 0.33.3, **daemon TẮT**, `~/.ollama/models` **rỗng** |
| Đĩa trống | 401 Gi — thừa cho 0.64 GB |
| Go toolchain | **không có** — nhưng không cần, xem dưới |
| plugin lumen | **chưa cài** (`~/.claude/plugins/cache/*/lumen*` không tồn tại) |
| MCP root hiện tại | `tavily-primary`, `tavily-backup`, `lsp` — chưa có `lumen` |
| Branch | `chore/cai-uv-pyenv-graphify`, cây **bẩn** (10 file chờ commit) |

Vậy phần "pull model" chỉ áp cho **local (backup)**; primary đã sẵn model.

### B2 — Nghiên cứu upstream (github.com/ory/lumen, Apache-2.0, đo theo 0.0.42)

**Không cần Go.** Release có sẵn binary đặt tên `lumen-<version>-<os>-<arch>`; đã kiểm
`https://github.com/ory/lumen/releases/download/v0.0.42/lumen-0.0.42-darwin-arm64` → **HTTP 200**.
`scripts/run` cũng tải đúng asset này khi thiếu `bin/lumen`.

**Failover là tính năng gốc của lumen**, không phải hack: `internal/config/service.go:23-30`
định nghĩa `ServerConfig{backend, host, model, dims, ctx_length, min_score}`, key YAML top-level là
`servers:` (list — **thứ tự = độ ưu tiên**), và `FailoverEmbedder` chuyển sang server sau khi
health-check server trước hỏng. Đường dẫn config: `config.go:128` →
`~/.config/lumen/config.yaml`.

**`qwen3-embedding:0.6b` nằm trong bảng model được hỗ trợ** của lumen: backend Ollama, dims 1024,
context 32768, cột trạng thái ghi *Untested*. Vì có trong bảng nên **không phải set
`LUMEN_EMBED_DIMS` tay**. Lưu ý "Untested" là nhãn của upstream — chất lượng search chưa được họ đo.

### Hai xung đột phải nói trước, không được giấu

1. **`tdq_lsp.py:42` hardcode `MODEL_LUMEN = "ordis/jina-embeddings-v2-base-code"`.**
   Bậc 5 của thang kiểm tra manifest model **ở local** theo đúng tên đó. Cấu hình lumen bằng
   `qwen3-embedding:0.6b` → bậc 5 **vẫn báo thiếu model**, dù lumen chạy hoàn hảo. Ba lối thoát,
   là quyết định của bạn: (a) sửa hằng số trong repo — đây là đổi code repo, (b) pull thêm
   `ordis/jina-embeddings-v2-base-code` (~330 MB) chỉ để làm hài lòng bậc 5, (c) chấp nhận bậc 5
   cảnh báo (bậc 5 vốn `chi_canh_bao=True`, không chặn gì). Plan mặc định chọn **(c)** và ghi rõ.

2. **Đường cài quyết định bậc 6 sống hay chết.** `skills/tdq-lsp-setup/references/lumen.md:56-58`:
   plugin lumen đăng ký hook `PreToolUse` trên `Grep`/`Bash` đẩy agent gọi lumen trước — đúng thứ
   mà **bậc 6 dò tìm**, và bậc 6 hiện đang ĐẠT. Cài bằng `/plugin install` → nhiều khả năng bậc 6
   chuyển thành FAIL, và bản cập nhật plugin sẽ đặt hook lại. Cài **binary trần + `claude mcp add
   --scope user`** thì không có hook nào → bậc 6 giữ nguyên. Plan chọn đường **binary trần**.

## Hỏi đáp

Chưa có câu hỏi chặn. Hai giả định đã nêu nguyên văn ở trên (ý nghĩa "model mặc định" cho phần
trích xuất; chọn lối (c) cho xung đột `MODEL_LUMEN`) — bạn phản đối thì tôi sửa plan trước khi làm.

### Q1 (11:55) — "lumen chỉ dùng search code thôi đúng không? comment tiếng Việt model mặc định handle tốt ko?"

**Không hẳn chỉ code.** `internal/chunker/languages.go:50` cho `.md`/`.mdx` vào danh sách index. Và quan
trọng hơn: comment **được cố ý gộp vào chunk** — `goast.go:39` parse với `parser.ParseComments`,
`declRange()` lấy `doc.Pos()` làm điểm bắt đầu; `treesitter.go:113-116` gọi `findLeadingComments()`
(tối đa 10 dòng, `maxLeadingCommentLines`). Nên comment tiếng Việt **có** đi vào vector.

**Model mặc định của lumen KHÔNG hợp tiếng Việt.** Mặc định là `ordis/jina-embeddings-v2-base-code`
(`models.go:26`) — jina-v2-base-code huấn luyện trên tiếng Anh + ~30 ngôn ngữ lập trình, phía ngôn ngữ
tự nhiên chỉ tiếng Anh. Comment tiếng Việt sẽ bị nhúng kém.

**Nhưng bạn không dùng mặc định.** `qwen3-embedding:0.6b` thuộc dòng Qwen3-Embedding đa ngữ (100+ ngôn
ngữ, có tiếng Việt) → chính lựa chọn của bạn đã xử lý sẵn vấn đề này. Đây là kiến thức nền của tôi về
dòng model, **chưa phải số đo trên máy này** — vì vậy thêm **T5b** vào plan để đo thật.

**Nếu T5b cho kết quả kém**, lối nâng cấp là `qwen3-embedding:8b` (bảng README: *Best quality*,
dims 4096, ctx 40960) — **không phải `:4b`**, upstream ghi thẳng *Not recommended* (over-retrieval nặng
với TypeScript, chi phí cao nhất). Đổi thì phải đổi **cả hai endpoint** vì dims khác nhau sẽ phá index.

### Q2 (12:02) — "đổi sang qwen3-embedding:8b; model truy xuất của lumen dùng gì?"

**Chốt model: `qwen3-embedding:8b`** cho cả hai endpoint (dims 4096, ctx 40960, min_score 0.30 —
`models.go:65`). Đo trên primary: **4.68 GB** (so với 0.6b = 0.64 GB, 4b = 2.5 GB). Máy này 24 GB RAM,
đĩa còn 401 Gi → chạy được. README xếp 8b là *Best quality* (7/9 wins) kèm cảnh báo **"very slow
indexing"**. Plan đã cập nhật T2/T3 + mục Rủi ro.

**Truy xuất KHÔNG dùng model riêng — và không dùng LLM nào cả.** Đã grep toàn `internal/`:
không có rerank, cross-encoder, hay lời gọi chat/completions. Đường truy xuất thực tế:

1. Câu truy vấn được nhúng bằng **chính model embedding đó** (`qwen3-embedding:8b`) — cùng một
   `Embedder`, cùng đường failover primary→backup.
2. Tìm KNN trong SQLite: bảng ảo `vec0(embedding <type>[4096] distance_metric=cosine)`
   (`store/shared.go:213-215`), lọc `knn.distance < maxDistance` (`shared.go:791`) — ngưỡng suy ra từ
   `min_score`, rồi mở rộng dần số candidate cho tới khi đủ `limit` (`shared.go:776-780`).
3. JOIN `chunk_defs` để trả về path + symbol + kind + dòng bắt đầu/kết thúc (`shared.go:807-810`).

Nghĩa là **chỉ có MỘT model trong toàn hệ thống**. "Trích xuất" (chunking) là AST/tree-sitter thuần,
không model; "truy xuất" là cosine trên vector, không model. Đây là lý do đổi model sau này bắt buộc
phải **index lại toàn bộ**: vector cũ 4096 chiều của model A không so sánh được với truy vấn của model B.

### Q3 (12:10) — "quay lại 0.6b; set model truy xuất thành qwen3.5:4b được không, có nên không?"

**Quay lại `qwen3-embedding:0.6b`** — plan đã sửa lại T2/T3/DoD#2/Rủi ro.

**Không set được, và cũng không nên.** Chứng cứ, không phải phỏng đoán:

- **Toàn bộ bề mặt cấu hình của lumen là 6 trường** (`service.go:24-29`): `backend`, `host`, `model`,
  `dims`, `ctx_length`, `min_score`. Đúng **một** trường `model`, và nó là model embedding. Không có
  trường thứ hai để gắn model sinh.
- **Toàn bộ biến môi trường**: `LUMEN_BACKEND`, `LUMEN_EMBED_MODEL/DIMS/CTX`, `LUMEN_MAX_CHUNK_TOKENS`,
  `LUMEN_VECTOR_STORAGE`, `LUMEN_FRESHNESS_TTL`, `LUMEN_REINDEX_TIMEOUT`, `LUMEN_LOG_LEVEL`,
  `LUMEN_ARTIFACT`. Không có biến nào cho model truy xuất/rerank.
- **lumen chỉ gọi 2 endpoint của Ollama**: `/api/tags` để health-check (`health.go:32`) và `/api/embed`
  để nhúng (`ollama.go:115`). **Không hề gọi** `/api/generate` hay `/api/chat` → không có đường nào để
  một model sinh như `qwen3.5:4b` tham gia.

Nhét `qwen3.5:4b` vào trường `model` cũng hỏng: nó là model **sinh (chat)**, không có embedding head cho
`/api/embed`; lại không nằm trong registry nên còn phải tự đặt `LUMEN_EMBED_DIMS`. Kết quả tốt nhất là
vector rác, tệ nhất là lỗi. Muốn có tầng rerank thật thì phải **vá source Go của lumen** — ngoài phạm vi
request này.

**Điều đáng nói:** vai trò "model hiểu câu hỏi" đã có rồi — chính là agent (tôi). Tôi diễn đạt truy vấn,
lumen chỉ làm phép so cosine. Thêm một LLM ở giữa không mua thêm được gì mà lumen cũng không hỗ trợ.
