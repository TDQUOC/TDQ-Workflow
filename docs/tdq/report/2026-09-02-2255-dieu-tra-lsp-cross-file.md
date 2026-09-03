# Báo cáo — Vì sao LSP không thấy caller khác file

**Ngày:** 2026-09-02 · Lane: quick · Plan: ../plan/2026-09-02-2255-dieu-tra-lsp-cross-file.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Câu hỏi: `find_callers` trên `scripts/tdq_state.py:303` (`load`) chỉ trả caller nằm trong
chính file đó, trong khi ground truth dựng bằng AST là **27 lệnh gọi ở 12 file**.

## 1. Server nào đang phục vụ, và nó nhận thư mục gốc nào

| Câu hỏi | Lệnh | Kết quả |
|---|---|---|
| Server Python là gì | `detect_lsp_servers` | **pyright-langserver** (`/opt/homebrew/bin/pyright-langserver`), cạnh đó có `vscode-json-language-server` và `vscode-html-language-server` |
| Nó đang index thư mục nào | `list_workspace_folders` | **`workspace_folders [0]` — rỗng, không một thư mục nào** |
| Nó khai báo làm được gì | `get_server_capabilities` | `referencesProvider`, `callHierarchyProvider`, `renameProvider` đều `true` |

Hai điều rút ra ngay:

- **Danh sách workspace folder rỗng.** Server khai có `callHierarchyProvider` và
  `referencesProvider`, nhưng không có gốc workspace nào để dựng chỉ mục trên đó. Pyright
  trả lời tham chiếu trong phạm vi các file đã mở, chứ không phải toàn dự án. Đây là lời giải
  thích khớp với triệu chứng: 13 caller tìm được đều nằm trong đúng file đã mở.
- **Thang `tdq_lsp.py kiem` không kiểm điều này.** Bậc 3 chỉ kiểm "có language server cho
  ngôn ngữ của project", và nó ĐẠT — vì pyright có thật. Không bậc nào hỏi "server có gốc
  workspace không".

## 2. Sửa lại một kết luận của phân tích ban đầu

Ở brief mục 4 tôi ghi `get_diagnostics` trên `hooks/scripts/stop_gate.py` trả **0 lỗi**, và
coi đó là dữ kiện đi ngược giả thuyết. **Điều đó sai và phải bỏ.**
`get_server_capabilities` liệt kê rõ:

> `UnsupportedTools[3]: format_range, get_diagnostics, type_hierarchy`

`get_diagnostics` **không được server này hỗ trợ**. Kết quả "0 lỗi" không phải là "file không
có lỗi" mà là "không ai trả lời câu hỏi". Nó chưa bao giờ là bằng chứng theo chiều nào cả.

Đây cũng là một cái bẫy đáng ghi riêng: công cụ trả về hình dạng thành công cho một năng lực
server không có. Một câu trả lời rỗng đọc y hệt một câu trả lời sạch.

## 3. Thí nghiệm quyết định — A/B/A

Cùng một câu hỏi (`find_callers` trên `scripts/tdq_state.py:303`), đổi đúng một biến mỗi lần.
Ground truth: **27 lệnh gọi ở 12 file**.

| Bước | Thay đổi | Số caller | Có caller ngoài file không |
|---|---|---|---|
| A | nguyên trạng | **13** | không — toàn bộ trong `tdq_state.py` |
| A′ | `add_workspace_folder` trỏ vào gốc repo | **13** | **không** — thêm workspace folder một mình **không đổi gì** |
| B | ghi tạm `pyrightconfig.json` khai `include: [scripts, hooks, tests]` và `extraPaths: [scripts, hooks/scripts]`, khởi động lại server | **34** | **có** — cả 5 file hook (`hooks/scripts.main` ×5) và nhiều hàm test |
| A″ | **xoá** `pyrightconfig.json`, khởi động lại server y hệt bước B | **13** | không — về đúng như cũ |

Bước A″ là phần quan trọng nhất: nó loại trừ khả năng "khởi động lại server mới là nguyên
nhân". Cùng một lệnh khởi động, chỉ khác có hay không có file cấu hình, kết quả 34 so với 13.

**Nguyên nhân gốc, đã chốt:** repo không có `pyrightconfig.json` (mục 2 của brief đã ghi nhận
repo cũng không có `pyproject.toml`, `setup.cfg`, `conftest.py`). Không có file nào khai
`scripts/` là gốc import, nên pyright không resolve nổi `import tdq_state` từ `hooks/` và
`tests/` — những nơi chèn `sys.path` lúc chạy. Không resolve được import thì không có cạnh
gọi, nên `find_callers` không thấy gì ngoài file hiện tại.

Vậy giả thuyết "đây là giới hạn thật của phân tích tĩnh với `sys.path` động" — nêu trong brief —
**sai**. Pyright lần ra được các caller đó, miễn là được chỉ đường bằng `extraPaths`.

Độ phủ sau khi sửa vẫn chưa đủ: 34 caller, thấy đủ 5 hook và nhóm test, nhưng
`tdq_team.py`, `tdq_timing.py`, `tdq_checkstatus.py` **không xuất hiện**. Cần nói rõ là output
của `find_callers` chỉ in namespace (`hooks/scripts.main`), **không in đường dẫn file và số
dòng**, nên không đối chiếu chính xác từng file được. Con số chắc chắn: **13 → 34 caller**,
từ không có caller ngoài file thành có. Không nên đọc thành "đã đủ 12/12".

## 4. Kết luận và khuyến nghị

1. **Sửa được, và rẻ.** Thêm `pyrightconfig.json` với `include` + `extraPaths` như ở bước B.
   Giá phải trả: một file cấu hình ở gốc repo. Không đổi code, không đổi cách chạy.
2. **Khuyến nghị của báo cáo `2026-09-02-2057` cần đọc lại sau khi có bản sửa này.** Báo cáo
   đó kết luận "bỏ LSP mất 0 %" dựa trên số đo khi LSP đang bị tàn tật vì thiếu cấu hình.
   Con số 0 % vẫn đúng với *hiện trạng*, nhưng không còn là cơ sở công bằng để bỏ LSP: phép
   đo lại sau khi thêm cấu hình mới cho biết LSP thật sự đáng giá bao nhiêu.
3. **Thang `tdq_lsp.py kiem` thiếu một bậc.** Nó báo 6/6 ĐẠT suốt trong khi chỉ mục liên file
   không hoạt động, vì mọi bậc đều kiểm **sự tồn tại** chứ không kiểm **hiệu quả**. Bậc còn
   thiếu: hỏi một câu có đáp án biết trước và so kết quả — đúng tinh thần "kiểm bằng hiệu ứng
   thật" của workflow này. Việc thêm bậc đó nằm ngoài phạm vi request này.
4. **Một cái bẫy cần nhớ**: `get_diagnostics` nằm trong `UnsupportedTools` của server này
   nhưng vẫn trả về kết quả rỗng trông như thành công (mục 2). Trước khi tin một câu trả lời
   rỗng của LSP, hãy hỏi `get_server_capabilities`.

Báo cáo này **không giữ lại thay đổi nào**: `pyrightconfig.json` đã xoá, `git status
--porcelain` chỉ còn file trong `docs/`.
