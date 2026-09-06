# Setup OmniSharp làm language server C#

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy setup omnisharp đi

Ngữ cảnh dẫn tới câu này (cùng phiên): người dùng hỏi LSP C# có chạy với **Unity trên Mac** không. Tôi trả lời csharp-ls yếu với Unity, và bảng khuyến nghị xếp **OmniSharp** ở hàng đầu vì nó nói stdio thuần (cắm thẳng vào args agent-lsp được) và hiểu Unity csproj. Người dùng chọn hướng (a) trong hai hướng tôi đề xuất.

### Cách tôi hiểu yêu cầu

- **Mục tiêu**: cài OmniSharp lên máy và đưa vào `args` của MCP `lsp` để `.cs` được phục vụ bởi OmniSharp thay vì csharp-ls.
- **Động cơ thật**: để code C#/Unity trên Mac có LSP dùng được — không phải để cải thiện repo TDQ-Workflow (repo này có **0 file `.cs`**).
- **Phạm vi đoán**: giống hệt request `2026-09-06-1326-them-language-server` — cài binary ở tầng máy, chứng minh bằng `agent-lsp doctor` trước khi ghi `~/.claude.json`, rồi cập nhật bảng `LANG_SERVER` trong `scripts/tdq_lsp.py`.

### Chỗ chưa rõ (phải hỏi hoặc điều tra ở pha analyze)

1. **Thay hay giữ csharp-ls?** agent-lsp chỉ nhận **một** server cho mỗi khoá ngôn ngữ, nên `csharp:omnisharp,...` sẽ **đẩy csharp-ls ra**. Cần người dùng chốt.
2. **Nguồn cài**: brew không có OmniSharp (đã tra `brew search omnisharp` → không ra). Phải tải release từ GitHub `OmniSharp/omnisharp-roslyn`, chọn asset `osx-arm64`. Cần hỏi quyền tải/cài như mọi lần.
3. **Phụ thuộc mono**: các bản OmniSharp có hai dòng asset (net6.0 tự chứa và bản cần mono). Chưa xác minh bản nào chạy được trên máy này — máy chỉ có .NET SDK 10.0.400, **không có mono**.
4. **Tình trạng dự án**: omnisharp-roslyn đã chậm phát triển sau khi Microsoft chuyển sang Roslyn LS. Cần kiểm release mới nhất còn dùng được không.
5. **Cách nghiệm thu**: máy **không có Unity** (`/Applications/Unity*` trống, không Unity Hub), nên không đo được hiệu ứng thật trên project Unity. Phải chốt tiêu chí nghiệm thu thay thế — ví dụ một project .NET tối thiểu có `.csproj`.
6. **Bẫy đã biết**: csharp-ls sập `abort trap` khi `list_symbols` lên file `.cs` mồ côi. Cần kiểm OmniSharp có dính lỗi tương tự không.

## Hiểu & kiến thức

<!-- pha analyze điền -->

## Hỏi đáp

<!-- pha analyze điền -->
