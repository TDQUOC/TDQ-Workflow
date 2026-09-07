# REPORT — Trang HTML trạng thái setup TDQ-Workflow (`2026-09-07-0905-trang-html-trang-thai-setup` · lane full · mode main · 20 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `scripts/setup_status.py` thu số liệu SỐNG (4 dependency, model+endpoint lumen, 9 skill trên đĩa, 64 dòng doc-surface của hook, 7 bậc LSP, state, `claude mcp list`, `agent-lsp doctor` khởi động thật 14 language server) · P2 `scripts/setup_status_render.py` kết xuất HTML tự chứa 4 khối, CSS nội tuyến, sáng/tối · P3 CLI ghi `setup_status.html` + gitignore · P4 log service + không hồi quy · P5 QC độc lập bằng agent `tdq-qc-tester` rồi 6 task fix.

**Kết quả:** trang 21K, 4 khối, dựng trong ~6 giây (phần lớn là dò sống 14 LSP) · đo thật trên máy: graphify 0.9.55 · lumen 0.0.42 (`qwen3-embedding:0.6b`, tailnet + localhost) · agent-lsp 0.19.2 · ollama 0.33.3 · 7/7 bậc ĐẠT · LSP khai 14 / sống 14 · 6 MCP đều Connected · **0 khoá Tavily rò** dù nguồn `~/.claude.json` có 2 khoá thật (trang hiện `tavilyApiKey=***`).

**Kiểm:** `python3 -m unittest discover -s tests -t tests -p 'test_*.py'` → **Ran 1599, failures=290 errors=4 skipped=14**, bằng đúng nền 1533/290/4 và `diff` danh sách ca đỏ với nền RỖNG · 65 ca mới cho 2 module này đều xanh · lint tự động: **chưa kiểm** (máy chưa cài `ruff`) · QC **11/11 mục DoD PASS** + QC-F1..F4 PASS, qua 2 vòng.

**Đầu ra:** [scripts/setup_status.py](scripts/setup_status.py) · [scripts/setup_status_render.py](scripts/setup_status_render.py) · [tests/test_setup_status.py](tests/test_setup_status.py) · [tests/test_setup_status_render.py](tests/test_setup_status_render.py) · `.gitignore` · trang sinh ra `setup_status.html` (gitignored: chứa đường dẫn máy, IP tailnet, danh sách MCP — repo public). Không sửa gì ngoài repo, không cần backup.

**QC bắt được gì:** agent độc lập nêu 4 khuyết tật ngoài DoD → sửa 3 (che khoá chỉ phủ query string, bỏ sót cờ CLI và biến môi trường; lệnh cài agent-lsp chép tay sai; `render()` ném `AttributeError` khi dict sai kiểu) và **bác 1**: đề xuất đếm dòng `[error] ... exited with error` của doctor là server chết — đo 3 lần cho thấy `Summary: 14 ok` và `rc=0` đứng yên còn tập server trong dòng `[error]` đổi liên tục (4 → 7 → 5), tức nhiễu lúc đóng tiến trình; đếm sẽ báo hỏng SAI. Thay bằng đối chiếu chéo `Summary` + returncode với số đếm từng server. Tự chấm QC-F4 lòi thêm vi phạm OCP (`render()` phải sửa thân hàm mới thêm được khối) → gộp `KHOI` thành bảng 4 cột. **Bản vá QC1.2 lại tự có bug**: regex neo `^` dùng `re.search` thiếu cờ `re.M` nên test xanh giả trong khi trang thật báo nhầm "không thấy dòng Summary" — bắt được nhờ sinh trang thật rồi soi, không tin test.

**Giới hạn:** (1) skill built-in của Claude Code nằm trong binary nên script không đọc được — trang nói thẳng bằng đúng một dòng, bảng chỉ liệt kê skill trên đĩa. (2) `.gitignore` KHÔNG CÓ TEST riêng, chỉ kiểm gián tiếp qua Q8 `git status`. (3) Chưa có lint tự động vì máy chưa cài `ruff`. (4) Trang chạy tay (`python3 scripts/setup_status.py`), cố ý không móc vào `tdq_finish.py` theo lựa chọn của bạn lúc interview. (5) Parser bám mẫu tối thiểu của `claude mcp list` / `agent-lsp doctor`; hai công cụ đổi định dạng thì trang ghi "không phân tích được" kèm nguyên văn chứ không bịa.

**Git:** chưa commit, chưa push. Nhánh `feature/trang-trang-thai-setup`, gốc `main`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 4 min | 4 min | 1 |
| spec | 57 min | 8 min | 1 |
| implement | 22 min | 22 min | 1 |
| qc | 29 min | 19 min | 1 |
| report | 5s | 0s | 1 |
| **Total** | **1h 51min** | **53 min** | |

Phase `spec` 57 phút wall clock nhưng chỉ 8 phút model time: 49 phút là chờ bạn duyệt, không phải máy chạy.
