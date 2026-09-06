# BÁO CÁO — Thêm 10 language server vào agent-lsp

Ngày: 2026-09-06 · Lane: full · Mode: main (inline) · Spec/plan: ĐÃ DUYỆT
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

Args của MCP `lsp` đi từ **4 lên 14 mục**, cả 10 mục mới đều `agent-lsp doctor` → `Status: ok`
(đo trong shell đăng nhập thật): csharp · dockerfile · go · javascript · typescript · yaml ·
html · css · markdown · eslint. 4 mục cũ (`c`, `cpp`, `json`, `python`) giữ nguyên chuỗi.

Binary cài mới: go 1.27.1 · gopls 0.23.0 · dotnet 10.0.400 · csharp-ls 0.27.0 ·
docker-language-server 0.20.1 · typescript-language-server 6.0.0 · typescript 5.9.3 ·
yaml-language-server 1.24.0. Bốn binary `vscode-*` đã có sẵn, không cài lại.

Trong repo: `scripts/tdq_lsp.py` thêm khoá `dockerfile` vào **cả hai** bảng `LANG_SERVER` và
`LANG_CONFIG` (giữ bất biến `set(LANG_CONFIG) == set(LANG_SERVER)`), và lệnh cài `go` đổi từ
`go install …` sang `brew install go gopls` kèm lý do gopls cần `go` lúc chạy. Đi đúng đỏ→xanh:
2 test mới đỏ trước, sau khi sửa 39/39 xanh.

`~/.zshrc` thêm 2 dòng `export` (DOTNET_ROOT + PATH cho `~/.dotnet/tools`) sau khi user duyệt —
`diff` xác nhận chỉ thêm ở cuối, không đụng dòng nào có sẵn.

## Ba điều không suôn sẻ, đều đã xử lý

1. **`npm i -g typescript` kéo về 7.0.2** — bản native tsgo, `lib/` không còn `tsserver.js`, nên
   `typescript-language-server` chết ngay; bản 6 của nó cũng đã bỏ cờ `--tsserver-path`. Ghim
   `typescript@5.9.3` là gỡ được, chuỗi args giữ đúng như spec.
2. **Tôi vi phạm luật thi hành số 7** — ghi mục `csharp:csharp-ls` vào `~/.claude.json` khi nó
   chưa qua thử khô. Agent QC bắt được; đã gỡ ra, và chỉ ghi lại sau khi thử khô đạt. Agent QC
   vòng 2 kiểm chéo bằng mtime của hai bản sao lưu, xác nhận lần này đúng thứ tự.
3. **Rủi ro R4 của spec đoán thiếu một nửa** — `csharp-ls` cần CẢ HAI biến, không chỉ `PATH`.
   Thiếu `DOTNET_ROOT` thì thoát mã 131 vì brew đặt runtime ở `libexec`, không ở chỗ mặc định.

## QC

**10/11 PASS** (Q1–Q8, Q10, Q11). Hai vòng QC độc lập bằng agent, vòng 2 không còn defect chặn.
Q9 (suite repo xanh) KHÔNG đạt và KHÔNG do request này: HEAD sạch đã 1521 test/292 fail, sau thay
đổi 1523/290, `comm` cho **0 test hỏng mới**; cụm 284 ca là `test_skill_router` trỏ tới đường dẫn
skill không còn tồn tại. Ghi ở T6.3, đề xuất mở request riêng.

## Còn hạn chế

- **Phải khởi động lại Claude Code** thì 14 mục mới có hiệu lực; tiến trình `agent-lsp` đang chạy
  vẫn giữ 4 args cũ.
- Hai dòng export chỉ có ở shell tương tác (giống cách repo cố ý làm với pyenv), không áp cho
  script hệ thống.
- Gói npm ghim theo node v24.20.0; đổi node bằng nvm thì phải cài lại 3 gói npm.
- Request này KHÔNG cải thiện thang LSP của chính repo TDQ-Workflow (repo có 0 file của cả 5
  ngôn ngữ) — đúng như spec §1 đã nói trước; giá trị nằm ở các project khác.
- Chưa commit gì: user chọn 7C, tự lo git.
