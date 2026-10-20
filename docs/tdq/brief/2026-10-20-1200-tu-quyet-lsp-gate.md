# BRIEF — Tự Quyết Định Xử Lý Cổng LSP Không Cần Hỏi Người Dùng (`2026-10-20-1200-tu-quyet-lsp-gate`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay bây giờ tôi muốn mở request handlle là những issue về lsp này bạn hoàn toàn có toàn quyền quyết đinh, nếu chỉ là doc, resreach thì có thể skip còn nếu là project develop hoặc code base lớn,... thì bạn hoàn toàn có quyền tự quyết định check và setup lsp phù hợp cho user-level, hãy set trong tdqworkflow và set trong skill setup để auto thêm vào instruction luôn để không cần hỏi người dùng như này nữa"
(Kèm ảnh chụp màn hình terminal bị dừng hỏi cổng blocker LSP tại bước intake mở request)
Bổ sung: "bổ sung là nếu thiếu lsp cho task cần thì agent có quyền tự động sreach và install, setup dependency còn thiếu để đảm bảo hoạt động đúng và đủ"
Bổ sung tiếp: "bổ sung thêm là sẽ có cơ chế đảm bảo rule đúng kể cả có qua compact, (có thể nhét vào state hoặc hook gì đó)"

## Hiểu & kiến thức

### 1. Phân tích hiện trạng & Điểm nghẽn
- **Hiện trạng**: Tại bước 1b và bước 3 của `tdq-intake` và `kiem-lsp-hieu-ung.md`, quy định cũ ghi: *"init refuses while a module is unproven; only the user may choose --bo-qua-lsp"*. Khi thiếu language server, hệ thống chỉ cảnh báo hoặc dừng hỏi người dùng. Ngoài ra, khi phiên hội thoại bị nén (`compact`), Agent dễ mất ngữ cảnh và quay lại hỏi xin phép.
- **Hệ quả**: Agent bị dừng cơ học để hỏi xin ý kiến người dùng về cổng LSP hoặc xin phép cài đặt dependency, gây ngắt quãng quy trình tự động.
- **Giải pháp**:
  - Trao toàn quyền tự quyết cho Agent xử lý cổng LSP và cài đặt dependencies:
    1. Với request là tài liệu (`docs`), nghiên cứu (`research`), dọn dẹp (`chore`), cài đặt MCP/công cụ ngoài: Tự động áp dụng `--bo-qua-lsp` kèm lý do kỹ thuật rõ ràng khi `init`.
    2. Với request phát triển phần mềm (`feature`, `bugfix`) hoặc codebase lớn: Agent tự quyết định chạy `tdq_setup.py`, kiểm tra cấu hình LSP user-level; nếu kịch bản kiểm chứng bị chặn do đặc thù mã nguồn (như tham chiếu nội tệp), Agent tự động phân tích và áp dụng `--bo-qua-lsp` để tiếp tục mở request.
    3. Nếu thiếu Language Server hoặc công cụ phụ thuộc của LSP cho task cần làm: Agent có toàn quyền tự động tìm kiếm, cài đặt và thiết lập dependency còn thiếu (qua `npm i -g`, `uv tool install`, `pipx`, `brew` hoặc binary release) để đảm bảo hoạt động đúng và đủ mà không cần hỏi người dùng.
    4. **Bảo toàn qua Compaction**: Tiêm nguyên tắc `LSP-Autonomy` vào khối neo phục hồi `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py` (khi `source=compact` hoặc `resume`), đảm bảo sau khi nén phiên Agent vẫn ghi nhớ quyền tự quyết này và không bao giờ dừng hỏi người dùng.
  - Đồng bộ điều luật vào `KHOI_HUONG_DAN` (`CLAUDE.md`), `skills/tdq-intake/SKILL.md`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `kiem-lsp-hieu-ung.md`, `tdq_state.py` và `session_start.py`.

### 2. Năng lực & công cụ
- `tdq-intake`: Sửa bước 1b, 3 và `kiem-lsp-hieu-ung.md`.
- `tdq-setup`: Cập nhật `KHOI_HUONG_DAN`, `uu-tien-tim-kiem.md` và `CLAUDE.md`.
- `tdq-state`: Tinh chỉnh câu thông báo trong `_cong_lsp`.
- `hooks/scripts/session_start.py`: Tiêm rule vào `[TDQ:ANCHOR]` bảo toàn sau compact.

## Hỏi đáp
- Toàn bộ phạm vi đã rõ ràng và được người dùng chỉ định dứt khoát.
