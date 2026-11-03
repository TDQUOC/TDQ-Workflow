# REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load

Ngày: 2026-07-30 · Slug: `2026-07-30-plugin-lazy-load`

## Nguyên văn yêu cầu

> okay 1 thì giữ tavily, 2. chọn playwright, 3 chọn graphify, 4 chọn hạng 1, 5 giữa
> tất cả, nhưng xử lí instruction để claude lazy load khi cần để gảim nhẹ context,
> xử lí cho user-level và xử lí chi tiết để model cấp thấp vẫn xử lí tốt

(Tiếp nối turn audit + ranking plugin cùng ngày — xem working log 2026-07-30.)

## Cách hiểu đầu tiên

Phán quyết của user cho 5 nhóm trùng tính năng:

| Nhóm | Giữ | Tắt |
|---|---|---|
| 1. Search web | tavily | firecrawl |
| 2. Browser | **playwright** (user chọn ngược đề xuất) | chrome-devtools-mcp |
| 3. Hiểu codebase | graphify | lumen, greptile |
| 4. Code review | built-in (/code-review, /security-review) | sonarqube (feature-dev:code-reviewer thuộc plugin feature-dev — nhóm 5 giữ) |
| 5. Còn lại (workflow/memory/plugin-dev/design/domain) | GIỮ TẤT CẢ | — |

Kèm 3 yêu cầu xử lý:
1. **Lazy-load**: instruction để Claude chỉ nạp/dùng nhóm 5 khi cần → giảm context.
2. **User-level**: áp dụng ở `~/.claude/` (settings + CLAUDE.md), không chỉ project này.
3. **Model thấp**: instruction viết đủ chi tiết, enum đóng, để model yếu vẫn làm đúng.

## Chỗ chưa rõ (cần phân tích/hỏi)

- Cơ chế lazy-load thật sự: skill description do harness tự nhét vào context — CLAUDE.md
  không chặn được; phương án khả thi là "tắt mặc định + bảng định tuyến khi nào bật lại
  bằng lệnh nào" vs "giữ bật + luật chỉ-nạp-khi-khớp". Cần chốt cơ chế.
- feature-dev nằm cả nhóm 4 (tắt agent reviewer?) lẫn nhóm 5 (giữ plugin) — tắt được
  từng agent trong plugin không, hay chỉ tắt/bật cả plugin?
- Sửa `~/.claude/CLAUDE.md` đụng task T7.2 còn treo (viết lại §10) — gộp hay tách?
- Danh sách domain-plugin (datarobot, astronomer, unreal, qt, …) tắt mặc định hay giữ bật?
