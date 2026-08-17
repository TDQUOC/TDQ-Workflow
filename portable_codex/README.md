# TDQ Workflow — bản portable cho Codex CLI

Bản này dùng ĐÚNG cơ chế native của Codex, không phải markdown đọc tay:

| Lớp | File trong bundle | Codex làm gì với nó |
|---|---|---|
| Skill | `.agents/skills/<tên>/SKILL.md` | tự quét, nạp dần theo `description` |
| MCP | `.codex/config.toml` | `[mcp_servers.<tên>]`, chỉ TÊN biến môi trường |
| Hook | `.codex/hooks.json` + `hooks/` | canh `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop` |
| Dự phòng | `workflow/NN-*.md` | cho harness KHÁC (Antigravity…) đọc tuần tự |

Cần Codex CLI >= 0.147.0. Bản cũ hơn vẫn dùng được `workflow/*.md`, nhưng không có
lớp native nào.

## Cài ở máy mới — làm theo đúng thứ tự này

Thứ tự quan trọng: **trust TRƯỚC, chạy SAU**. Project chưa được tin cậy thì Codex bỏ qua
TOÀN BỘ tầng `.codex/` — MCP không nạp, `hooks.json` không đọc, bundle trông như rỗng mà
không báo lỗi gì.

1. **Chép** trọn nội dung thư mục này vào gốc project.
2. **Trust thư mục project** — xem ba cách ngay mục dưới.
3. **Kiểm**:
   ```
   python3 scripts/tdq_checkportable.py check
   ```
   Kết quả có một dòng nói project đã trusted hay chưa. Đọc theo tiền tố: `SẠCH` xong ·
   `THIẾU` chưa có · `LỆCH` khác manifest · `LƯU Ý` việc chỉ bạn làm được.
4. **Vá** nếu có `THIẾU`/`LỆCH`: `python3 scripts/tdq_checkportable.py setup` — nó dựng lại
   hai file cấu hình tái tạo được, luôn sao lưu `<file>.tdq-bak-<timestamp>` trước khi ghi
   đè, và báo `CÒN …` cho phần chỉ chép lại từ bản gốc mới đúng.
5. **Đặt biến môi trường** cho MCP nếu `check` báo thiếu. Script cố ý KHÔNG làm hộ việc này
   và không bao giờ in giá trị khoá — chỉ báo tên biến.
6. **Mở Codex CLI** trong project, rồi **khởi động lại phiên** một lần để skill trong
   `.agents/skills/` được quét.
7. **Duyệt hook** trong giao diện Codex — cổng RIÊNG, xem mục "Bốn việc" bên dưới.
8. **Duyệt MCP server** — mỗi server một lần.

## Trust — ba cách, chọn một

**Cách 1 — để script làm, không cần mở Codex:**

```
cd <gốc project đã chép bundle vào>
python3 scripts/tdq_checkportable.py setup --trust
```

**Cách 2 — bấm trong Codex:** mở Codex CLI ngay tại thư mục project; lần đầu vào thư mục lạ
nó hỏi có cho phép làm việc ở đây không → chọn phương án tin cậy thư mục.

**Cách 3 — sửa tay** `~/.codex/config.toml` (hoặc `$CODEX_HOME/config.toml`), thêm:

```toml
[projects."/đường/dẫn/tuyệt/đối/tới/project"]
trust_level = "trusted"
```

Đường dẫn phải TUYỆT ĐỐI và đã resolve symlink, khớp đúng thư mục Codex chạy trong đó —
lệch một ký tự là không ăn.

Cách 1 chính là đường DUY NHẤT của bộ này ghi ra ngoài bundle: nó luôn để lại
`<file>.tdq-bak-<timestamp>`, giữ nguyên phần còn lại của file, và không ghi chồng block đã
có. Không có cờ `--trust` thì `setup` không đụng tới file đó.

Kiểm đã ăn chưa: chạy lại `check` và đọc dòng trạng thái trusted.

## Bốn việc máy KHÔNG tự làm được

1. **Tin cậy thư mục** — `setup --trust` làm thay được (Cách 1 ở trên), hoặc bấm đồng ý
   trong Codex.
2. **Duyệt hook** — hook có cổng tin cậy RIÊNG: Codex hiện "Review hooks" trong giao diện và
   bạn phải duyệt một lần. `--trust` không mở được cổng này, và sửa `hooks.json` thì phải
   duyệt lại. Chưa duyệt thì hook im lặng không chạy.
3. **Duyệt MCP server** — mỗi server trong `.codex/config.toml` cần bạn duyệt một lần.
4. **Khởi động lại** — instruction mới chỉ được nạp sau khi khởi động lại phiên.

## Vì sao bước 3 chạy thẳng file, không nhắn "chạy skill tdq-checkportable"

Skill nằm trong chính bundle này, mà Codex chỉ quét `.agents/skills/` sau khi project được
tin cậy và phiên đã khởi động lại. Gọi skill ở bước đầu là vòng luẩn quẩn; chạy thẳng
`python3 scripts/tdq_checkportable.py` bằng terminal thì không vướng. Từ lần sau, khi mọi
thứ đã nạp, gọi skill bình thường.

## Khoá bí mật

Không file nào ở đây chứa giá trị khoá, chỉ TÊN biến môi trường (`env_vars` trong
`config.toml`). Tự đặt biến ở máy mình trước khi dùng MCP.
