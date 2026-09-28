# Research — 2026-09-28-0910-lumen-check-va-setup-tool

Phiên không có MCP `tavily-primary`. Công cụ đã dùng: `WebSearch` + `WebFetch`
(nạp schema qua `ToolSearch`), thêm `curl` cho raw README và GitHub API của
`ory/lumen`.

## 1. `~/.claude/CLAUDE.md` có hỗ trợ import `@path/to/file` không, giới hạn gì?

- Truy vấn: docs Claude Code trang memory, mục "Import additional files".
- Nguồn: https://code.claude.com/docs/en/memory (redirect từ
  docs.claude.com/en/docs/claude-code/memory)
- Kết quả:
  - CÓ. "CLAUDE.md files can import additional files using `@path/to/import`
    syntax." File được import expand và nạp vào context lúc launch.
  - Cho phép CẢ đường dẫn tương đối và tuyệt đối. Tương đối giải theo file
    CHỨA import, không theo working directory.
  - Import lồng nhau được, "with a maximum depth of four hops" (tối đa 4 chặng).
  - Parser BỎ QUA code span và fenced code block. Muốn nhắc đường dẫn mà không
    import thì bọc backtick: `` `@README` `` là văn bản, `@README` là import.
  - Áp dụng cho cả user-level: doc nêu ví dụ `- @~/.claude/my-project-instructions.md`
    và gọi `~/.claude/CLAUDE.md` là "User-scope memory files".
  - Khác biệt quan trọng về tin cậy: import trong file memory PROJECT trỏ ra
    ngoài working directory bị coi là "external" → có hộp thoại xin duyệt một
    lần; nếu từ chối thì import tắt vĩnh viễn. File user-scope
    (`~/.claude/CLAUDE.md`, `~/.claude/rules/`) được nạp import KHÔNG cần hộp
    thoại — trừ phiên Cowork trên desktop.
  - Cowork trên desktop: bỏ qua import trong file user-scope trỏ ra ngoài
    working directory, và bỏ qua `~/.claude/CLAUDE.md` nếu chính nó là symlink
    hoặc hard link.
- Suy ra cho request: có thể chẻ `~/.claude/CLAUDE.md` thành nhiều file nhỏ và
  import bằng `@~/.claude/...`, không bị hộp thoại duyệt. Nhưng KHÔNG tiết kiệm
  context: doc ghi rõ "imported files still load and enter the context window
  at launch". Giữ lồng nhau ≤ 4 chặng. Mọi đường dẫn nhắc-mà-không-import phải
  bọc backtick, nếu không sẽ thành import ngoài ý muốn.

## 2. Có cách tắt/ghi đè hook của plugin khác mà không sửa file plugin?

- Truy vấn: docs Claude Code trang hooks, tìm `disabledHooks`, `disableAllHooks`,
  thứ tự ưu tiên settings.
- Nguồn: https://code.claude.com/docs/en/hooks và
  https://code.claude.com/docs/en/settings#settings-precedence
- Kết quả:
  - KHÔNG có khoá `disabledHooks` và KHÔNG có cách tắt một hook riêng lẻ. Doc
    nói thẳng: "There is no way to disable an individual hook while keeping it
    in the configuration."
  - Chỉ có công tắc tổng `"disableAllHooks": true` trong settings — tắt TẤT CẢ
    hook, kể cả hook của plugin. Giá trị đọc sau khi áp settings precedence, nên
    `false` ở `.claude/settings.json` của project ghi đè `true` ở user settings.
  - Một lần chạy: `claude --settings '{"disableAllHooks": true}'`.
  - Giới hạn: `disableAllHooks` ở user/project/local KHÔNG tắt được hook do
    managed policy settings của admin cấu hình.
  - Suy ra: muốn bỏ đúng một hook của plugin mà không sửa file plugin thì chỉ
    còn đường tắt hẳn plugin đó (bỏ khỏi danh sách plugin đang bật), không có
    cơ chế ưu tiên hay override ở mức hook.
- Suy ra cho request: hook `PreToolUse` của lumen (cái chèn "dùng
  semantic_search thay Grep") không thể tắt riêng bằng `settings.json`. Lựa
  chọn: chịu, hoặc tắt cả plugin lumen, hoặc sửa `hooks/hooks.json` trong
  plugin (bị ghi lại mỗi lần update plugin). Đừng thiết kế giải pháp dựa trên
  một khoá `disabledHooks` — nó không tồn tại.

## 3. Lumen cập nhật index thế nào, staleness đo bằng gì, có bẫy "fresh" giả?

- Truy vấn: README + docs/INDEX_STORAGE.md của `ory/lumen`, và GitHub API tìm
  issue/PR có chữ "stale".
- Nguồn: https://github.com/ory/lumen (README),
  https://github.com/ory/lumen/blob/master/docs/INDEX_STORAGE.md,
  https://github.com/ory/lumen/pull/63
- Kết quả:
  - Cơ chế: index tự chạy lúc session start; Lumen đi bộ cây file và dựng
    **Merkle tree trên hash của file**, chỉ file đổi hash mới bị chunk và embed
    lại. Không dùng mtime.
  - `semantic_search` CÓ tự index: README ghi "The first `semantic_search` call
    seeds or refreshes the index automatically"; mô tả tool trong phiên này
    cũng ghi "Auto-indexes if the index is stale or empty".
  - `index_status` có cột `stale` = "Whether the source tree differs from the
    stored Merkle state" (so với trạng thái Merkle đã lưu, phạm vi project).
  - BẪY QUAN TRỌNG — freshness TTL cache: PR #63 thêm `LUMEN_FRESHNESS_TTL`,
    **mặc định 60s**: "successive `semantic_search` calls skip the Merkle tree
    rebuild when the index was confirmed fresh recently". Nghĩa là trong ~60s
    sau một lần xác nhận fresh, lệnh search KHÔNG dựng lại Merkle → nội dung
    vừa ghi vào một file ĐÃ từng index sẽ không có trong kết quả, mà hệ thống
    vẫn tự coi là fresh.
  - Bẫy thứ hai — donor seeding giữa các worktree: index của worktree mới được
    seed bằng cách copy từ worktree chị em; PR #63 mô tả bản ghi file "lạc"
    (ví dụ `.md` từ binary cũ) tích tụ trong DB và sinh diff "removed" ảo.
  - Hai tình huống tạm ngắt search: PR #163 "short-circuit `semantic_search`
    when index is being rebuilt" và PR #165 "fast-fail during background
    reindex" → search có thể trả rỗng/lỗi trong lúc đang rebuild, không phải
    "không có kết quả".
  - Cách buộc làm lại: `/lumen:reindex` trong Claude Code, hoặc
    `lumen index --force .`.
- Suy ra cho request: khi kiểm lumen, đừng tin `stale: false` ngay sau khi vừa
  sửa file — chờ quá TTL 60s, hoặc hạ `LUMEN_FRESHNESS_TTL`, hoặc chạy
  `/lumen:reindex` trước khi kết luận index thiếu nội dung. Nếu thấy search
  rỗng, phải loại trừ trường hợp đang rebuild trước khi kết luận index sai.

## 4. `qwen3-embedding:0.6b`: context, dims, chất lượng trên truy vấn CODE?

- Truy vấn: model card Hugging Face, blog chính thức Qwen, technical report, và
  bảng model được hỗ trợ trong README của lumen.
- Nguồn: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B,
  https://qwenlm.github.io/blog/qwen3-embedding/,
  https://arxiv.org/pdf/2506.05176, https://github.com/ory/lumen (bảng model)
- Kết quả:
  - Context length: **32K token** (32768). Dims: **tối đa 1024**, cho phép tự
    đặt trong khoảng 32–1024 nhờ MRL (Matryoshka). Có instruction-aware.
  - Điểm code: MTEB-Code của 0.6B = **75.41**. MTEB multilingual mean của 0.6B
    = 64.33 (so với 4B 69.45 và 8B 70.58) → tức trên code nó không tệ, nhưng
    thua rõ các bản lớn ở tổng thể.
  - Instruct: nên thêm instruction cho QUERY, "no need to add instruction for
    retrieval documents"; có instruction thường thêm 1–5%.
  - Lumen tự đánh giá: bảng model của README ghi `qwen3-embedding:0.6b` |
    Ollama | Dims 1024 | Context 32768 | khuyến nghị = **"Untested"**. Mặc
    định của lumen là `ordis/jina-embeddings-v2-base-code` (768 dims, ctx 8192,
    "Best default — lowest cost, no over-retrieval"); bản "Best quality" là
    `qwen3-embedding:8b`. Lưu ý `qwen3-embedding:4b` bị đánh dấu
    **"Not recommended"** (chi phí cao nhất, over-retrieval TypeScript nặng).
  - Về việc "yếu ở truy vấn tên ký hiệu chính xác": **KHÔNG KẾT LUẬN ĐƯỢC** cho
    riêng model này — không có khuyến cáo chính thức nào của Qwen nói vậy. Chỉ
    có khuyến cáo ở tầng công cụ: README lumen nói search theo "meaning, not
    keyword matching", và mô tả tool `semantic_search` dặn dùng Grep/Glob cho
    "exact literal string" đã biết. Đây là đặc tính của dense retrieval nói
    chung, không phải nhược điểm riêng của qwen3-embedding:0.6b.
- Suy ra cho request: dùng `qwen3-embedding:0.6b` thì phải nhớ đây là lựa chọn
  "Untested" theo chính lumen — không có số benchmark nội bộ nào của lumen cho
  nó. Nếu ưu tiên độ tin cậy đã đo, đổi về mặc định
  `ordis/jina-embeddings-v2-base-code`. Với truy vấn là tên hàm/ký hiệu chính
  xác, vẫn nên dùng Grep song song — nhưng lý do là bản chất dense retrieval,
  đừng ghi vào tài liệu như thể Qwen đã khuyến cáo.
