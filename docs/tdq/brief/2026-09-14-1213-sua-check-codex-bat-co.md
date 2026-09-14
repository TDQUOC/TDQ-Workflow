# BRIEF — Sửa `check` của Codex và lệnh bật cờ đồng ý
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1a

Câu trả lời cho câu hỏi "mở request sửa hai lỗi" ở cuối turn trước. Nội dung phương án A được chọn:
"mở request `bugfix`: `check` gửi say hi thật, lệnh bật cờ chạy được ở gốc repo, và chạy nốt Q13
cùng Q21b".

Yêu cầu gốc của request trước, nguyên văn, là căn cứ của lỗi 1: "khi gọi codex implement cũng sẽ
gọi check codex say hi xem có trả về ko nếu có thì lúc chọn mode mới show codex implement".

### Đọc lần đầu

- **Mục tiêu:** cổng chọn mode chỉ cho chọn `codex implement` khi Codex THẬT SỰ trả lời được, và
  người dùng bật được cờ đồng ý bằng đúng một lệnh đã ghi trong tài liệu.
- **Phạm vi đoán:** `scripts/tdq_codex.py` (hàm `_kiem_song` và lệnh bật cờ), có thể
  `scripts/tdq_checkportable.py`, test đi kèm, các chỗ tài liệu đang chỉ lệnh bật cờ, rồi chạy thật
  Q13 và Q21b của spec `2026-09-10-2247-mode-codex-implement`.
- **Chỗ chưa rõ:** lệnh bật cờ nên nằm ở `tdq_codex.py` hay sửa `tdq_checkportable.py` để chạy
  được không cần `manifest.json`; kiểm sống thật tốn 5–11s và gọi mạng mỗi lần hỏi mode, có nên nhớ
  kết quả trong một khoảng thời gian không; timeout của phép kiểm bao nhiêu thì báo "không chạy được".

### Bằng chứng phân loại lỗi (đã đo 2026-09-14)

| Lỗi | Triệu chứng | Nơi | Điều kiện kích hoạt | Phạm vi ảnh hưởng |
|---|---|---|---|---|
| 1 | `check` báo `chay_duoc: true` khi model không trả lời được | `scripts/tdq_codex.py:125-144` — `_kiem_song` chỉ chạy `codex --version` | Router hoặc model chết, `codex` vẫn cài | Cổng chọn mode mời một mode không chạy được; người dùng biết lúc đang implement |
| 2 | `setup --codex` in `ERROR no manifest.json` rồi exit 1, không ghi cờ | `scripts/tdq_checkportable.py:141-146` (`doc_manifest`) gọi trước `cai_tang_codex` | Chạy ở gốc repo nguồn, nơi không có `manifest.json` | Lệnh bật cờ ghi trong report, QC và câu `goi_y` của `check` đều không chạy được ở repo này |

Tái hiện lỗi 1: cho `CODEX_HOME` trỏ vào một `config.toml` có `base_url` là cổng chết
`127.0.0.1:1`. `check --json` trả `{"co": true, "chay_duoc": true, "phien_ban": "codex-cli 0.154.0"}`,
trong khi một lượt `codex exec` cùng cấu hình **quá hạn 60s**. Với router thật đang sống, một lượt
say hi trả `hi` sau 11.5s.

Tái hiện lỗi 2: `python3 scripts/tdq_checkportable.py setup --codex` ở gốc repo → `ERROR no
manifest.json found in …`, exit 1, `docs/tdq/.tdq-codex.json` không được tạo.

Trạng thái máy lúc mở: cờ đồng ý đã bật tay ở turn trước bằng chính hàm `tdq_codex.dat_co_dong_y`,
`codex_model = ag/gemini-3.8-flash-medium`, `check` và `modes --json` báo 3 mode chọn được.

### Lớp tìm kiếm

`tdq_lsp.py check` 7/7 bậc ĐẠT. Kiểm hiệu ứng trên `dat_co_dong_y`: grep 4 file, LSP
`find_references` 12 tham chiếu quy về 4 file (3 ở `scripts`, 9 ở `tests`, khớp số đếm từng file
của grep) → ĐẠT.

## Hiểu & kiến thức

Lane quick, loại `bugfix`, nhánh `bugfix/sua-check-codex-bat-co` từ `main`.
Vòng scope: BỎ — request chỉ đích danh bốn hành vi đã tái hiện, mọi mặt khác suy ra được từ code.
Bỏ B0: `scripts/tdq_codex.py` và `tdq_checkportable.py` đã có report `2026-09-10-2247-mode-codex-implement`.
Bỏ B2: không có ẩn số ngoài repo, hành vi Codex đã đo trực tiếp trên máy.

### Bốn lỗi, không phải hai

| # | Lỗi | Bằng chứng |
|---|---|---|
| 1 | `check` chỉ chạy `codex --version` | router chết → `chay_duoc: true`, lượt thật quá hạn 60s |
| 2 | Lệnh bật cờ gãy ở gốc repo | `main()` của `tdq_checkportable.py` đọc manifest trước khi tới `cai_tang_codex` |
| 3 | `run` không gọi được model trên máy này | `dung_codex_home` chỉ ghi `model = …` và chép `auth.json`; Codex rơi về provider `openai` → `400 model not supported when using Codex with a ChatGPT account` (đo 9.1s) |
| 4 | Thư mục `CODEX_HOME` tạm KHÔNG bị gitignore | `git check-ignore docs/tdq/.tdq-codex-home/…/auth.json` → NOT IGNORED; repo công khai, `run` chết giữa chừng thì `auth.json` nằm lại |

Lỗi 3 là lý do Q13 và Q21b chưa bao giờ chạy được. Nó cũng buộc phép say hi của `check` phải đi
qua đúng `CODEX_HOME` tạm mà `run` dùng; kiểm bằng `~/.codex` thật sẽ lại báo sai y như lỗi 1.

### Điều đã biết từ code

- Cấu hình máy: `model_provider = "9router"`, bảng `[model_providers.9router]` có `base_url`,
  `wire_api` và bảng con `http_headers` chứa `Authorization` là khoá sống. Bảng `[agents]` và
  `[projects.*]` không cần cho một lượt gọi.
- Cổng mode gọi `check` qua `_probe_codex` (`scripts/tdq_state.py:1310`, timeout 60s). Hook
  `prompt_context.py:224` chỉ dò khi đang chờ chọn mode, không dò mỗi prompt. Hook
  `UserPromptSubmit` không khai timeout, nên mặc định 60s.
- Câu `goi_y` của nguyên nhân 2 nằm ở ba chỗ: `tdq_codex.py:162`, `CAU_HOI_CODEX` trong
  `tdq_checkportable.py`, và bảng 4 nguyên nhân trong `skills/tdq-plan/references/mode-gate.md`.
- Test `tests/test_codex_cli.py` giả `_kiem_song` bằng `mock.patch.object`, nên đổi thân hàm không
  vỡ các test cũ của `check`.

## Hỏi đáp

Vòng chi tiết, 2026-09-14 12:3x. Người dùng trả lời nguyên văn: "1a 2a 3a 4a".

| # | Câu hỏi | Chọn | Hệ quả |
|---|---|---|---|
| 1 | `CODEX_HOME` tạm lấy cấu hình provider thế nào | A | Chép `model_provider` và bảng `[model_providers.<tên>]` kèm bảng con; bỏ `[agents]`, `[projects]`; gitignore thư mục tạm |
| 2 | Lệnh bật cờ đồng ý đặt ở đâu | A | Lệnh mới `tdq_codex.py dong-y --model <tên>`; `setup --codex` của bundle gọi cùng hàm; sửa ba chỗ gợi ý |
| 3 | Chi phí say hi | A | Không nhớ kết quả; timeout 30s; sandbox chỉ đọc; đạt khi exit 0 và câu trả lời không rỗng |
| 4 | Bổ sung thêm | A | Không bổ sung |
