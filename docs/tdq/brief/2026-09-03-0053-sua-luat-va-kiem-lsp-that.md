# Sửa luật thứ tự tìm kiếm + bắt kiểm LSP hoạt động thật trước khi làm việc

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1a và bổ sung thêm luật check lsp và config lsp và make sure nó hoạt động trước khi đi vào
> làm việc để make sure nó có hoạt động

Option 1a đã chọn, nguyên văn:

> mở request sửa luật `uu-tien-tim-kiem.md` — phân theo loại truy vấn (quan hệ → LSP trước,
> tên chính xác → grep trước, khái niệm → lumen trước) thay vì bắt buộc gọi song song

Đọc lần đầu — **hai phần**:

1. **Sửa luật thứ tự tìm kiếm.** Bỏ câu "BẮT BUỘC gọi song song `mcp__lsp__*` và lumen ở mọi
   truy vấn ký hiệu code", thay bằng bảng phân theo **loại truy vấn**, dựa trên số đo của
   báo cáo `2026-09-03-0017`:
   - quan hệ / đổi tên / blast radius → LSP trước (độ phủ 15/15, precision 100 %)
   - tên chính xác đã biết token → grep trước (nhanh gấp ~30–60 lần, đủ 100 %)
   - khái niệm mơ hồ, không có tên để bám → lumen trước (LSP xếp đích hạng 13/62)
   Sửa ở file gốc `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`, 5 chỗ móc chỉ trỏ
   về nên tự khớp — nhưng `tests/test_tdq_lsp_skill.py` so **câu trích nguyên văn**, nên đổi
   câu đó là phải sửa cả 5 chỗ móc lẫn test.
2. **Thêm luật kiểm LSP thật sự hoạt động trước khi vào việc.** Đây là phần user thêm mới, và
   là bài học trực tiếp từ 3 request vừa rồi: thang `tdq_lsp.py kiem` báo **6/6 ĐẠT** trong cả
   trạng thái độ phủ 7 % lẫn 100 %. Nó kiểm **sự tồn tại**, không kiểm **hiệu quả**. Cần:
   - một bậc kiểm **cấu hình gốc import** theo ngôn ngữ (Python: `pyrightconfig.json` /
     `pyproject.toml`; TS: `tsconfig.json`; Go: `go.mod`; Rust: `Cargo.toml`…)
   - một bậc kiểm **bằng hiệu ứng thật**: hỏi một câu có đáp án biết trước, so kết quả. Đây là
     bậc duy nhất phát hiện được lỗi kiểu 7 % ↔ 100 %.
   - và luật: **chạy kiểm này trước khi vào việc**, không phải chỉ ở intake.

**Phạm vi đoán**: `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` (file gốc, 93 dòng);
`skills/tdq-lsp-setup/SKILL.md` (116 dòng, mô tả thang 6 bậc); 5 chỗ móc trong `tdq-intake` ×2,
`tdq-spec`, `tdq-plan`, `tdq-build`; `scripts/tdq_lsp.py` (451 dòng) thêm bậc; `tests/
test_tdq_lsp.py` (311 dòng) và `tests/test_tdq_lsp_skill.py` (81 dòng); `skills/tdq-lsp-setup/
references/languages.md`; 3 bundle portable vì `skills/` đổi; có thể cả
`docs/tdq/audit/luat-hien-co.md` nếu đếm dòng lệch.

**Rủi ro đã biết**:
- Bậc kiểm bằng hiệu ứng cần một câu hỏi có đáp án cố định — nếu neo vào
  `scripts/tdq_state.py:303` thì code đổi là bậc đỏ giả. Phải chọn cách neo không giòn.
- Bậc kiểm hiệu ứng phải gọi MCP `lsp`, mà `tdq_lsp.py` là script Python chạy ngoài agent —
  script không gọi được tool MCP. Đây là ràng buộc kỹ thuật **chưa có lời giải**, phải chốt
  trước khi lên plan.
- "Kiểm trước khi vào việc" mỗi lượt sẽ tốn thêm thời gian mỗi request — phải cân với động cơ
  "chậm" mà user đã nêu ở request 2057.

**Chỗ chưa rõ**: xem mục Hỏi đáp.

## Hiểu & kiến thức

### Năng lực dùng được

| Nguồn | Năng lực | Phán quyết |
|---|---|---|
| `skill_inventory.py --loc` | lọc theo từ khoá → **giữ 0 / ẩn 217** | không skill nào trên đĩa khớp; không có tiền lệ đóng gói sẵn cho việc này |
| plugin `tdq-workflow` | `tdq-lsp-setup` (chủ đề chính), `tdq-conventions`, `tdq-spec/plan/build` | **DÙNG** — `tdq-lsp-setup` là file bị sửa; 5 skill kia là chỗ móc |
| MCP `lsp` | 66 tool code intelligence | **DÙNG** — vừa là công cụ đọc code, vừa là đối tượng của request |
| MCP `lumen` | `semantic_search` | **DÙNG** — lớp thứ ba trong luật đang sửa |
| MCP `tavily-primary` | tìm nguồn ngoài | **ĐÃ DÙNG** — xem `docs/tdq/research/2026-09-03-0053-*.md` |
| built-in `Read/Grep/Bash` | đọc file, chạy test | **DÙNG** |
| built-in Agent | sub-agent | **BỎ** — harness của phiên này cấm gọi Agent khi user không yêu cầu; research 2 truy vấn tự chạy, digest đã tách ra file riêng đúng tinh thần tiết kiệm context |

### Đọc code — hiện trạng

- `scripts/tdq_lsp.py` (451 dòng): 6 bậc, mỗi bậc một hàm `bacN_*` trả `Bac(...)`, gom ở
  `chay_kiem()` dòng 310–317. Bậc 1–4 chặn (`EXIT_THIEU`), bậc 5–6 chỉ cảnh báo. Thêm bậc 7 là
  thêm 1 hàm + 1 phần tử trong list — cấu trúc đã sẵn sàng, không phải sửa kiến trúc.
- `do_ngon_ngu(project)` dòng 196 đã đếm file theo ngôn ngữ và lọc ngưỡng 3 file. Bậc mới
  **dùng lại nguyên hàm này**, không phải quét lại cây thư mục.
- `LANG_SERVER` dòng 67–96 phủ 27 ngôn ngữ. Bảng cấu hình mới phải khớp đúng bộ khoá này.
- `tests/test_tdq_lsp_skill.py` (81 dòng) so **câu blockquote đầu tiên** của §1 file luật gốc
  với 5 chỗ móc, sau khi chuẩn hoá khoảng trắng. Ba test khoá: câu đủ 3 lớp đúng thứ tự
  LSP→lumen→grep; 5 chỗ móc chứa nguyên văn; §5 file gốc nhắc đủ 5 tên file.
- **Điểm cần chú ý**: `test_cau_goc_du_ba_lop` khoá thứ tự chữ `mcp__lsp__` < `lumen` < `grep`
  trong câu. Luật mới phân theo loại truy vấn nên **không còn một thứ tự tuyến tính duy nhất** —
  test này phải sửa theo, không chỉ sửa file luật.
- `skills/tdq-lsp-setup/SKILL.md` dòng 113–114 **đã có sẵn** ý "kiểm bằng hiệu ứng":
  *"one `mcp__lsp__*` call returns the right file and line for a real function in the repo"*.
  Nhưng nó nằm ở dòng "Done when" của skill, không được móc vào intake và không ai kiểm.
  Việc cần làm là **nâng câu này thành bước bắt buộc có bằng chứng**, không phải phát minh mới.
- `docs/kien-truc.md` luật gọi: `skills/` chỉ được nhắc TÊN LỆNH của `scripts/`, cấm chép nội
  dung script vào skill. Ràng buộc này chi phối cách viết luật mới.

### Research — đã chạy, kết quả ở file riêng

`docs/tdq/research/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md`. Hai điều quyết định thiết kế:

1. Mọi client LSP tìm gốc dự án bằng **root marker** — một file mốc theo ngôn ngữ. Nguồn:
   tài liệu gopls, rust-analyzer, LuaLS, và phân tích module LSP của opencode.
2. Ngôn ngữ chia **hai nhóm**. Nhóm A (Go, Rust, Java, C#, Ruby, PHP…) có file mốc là manifest
   build — thiếu thì dự án không build được, tự lộ. Nhóm B (**Python, TypeScript/JavaScript,
   Lua, C/C++**) cấu hình là tuỳ chọn — thiếu thì **hỏng âm thầm**, test vẫn xanh. Repo này sập
   đúng ở nhóm B.

### Ràng buộc đã chốt

- Script Python không gọi được tool MCP → bậc "kiểm bằng hiệu ứng thật" **không thể** là bậc
  script. User đã chọn **3a**: script kiểm cấu hình, luật trong skill lo phần hỏi-thử.
- User đã chọn **2a**: kiểm một lần mỗi request, ở intake — không thêm độ trễ cho từng truy vấn.

## Hỏi đáp

- Lane → user chọn **A: chuyên sâu (deep)**.
- Chỗ chạy kiểm → user chọn **2a: một lần mỗi request, ở intake**.
- Cách giải bài toán script-không-gọi-được-MCP → user chọn **3a: script kiểm cấu hình gốc
  import theo ngôn ngữ; phần hỏi-thử-một-câu là luật trong skill**.
- Vòng phạm vi: BỎ. Lý do — user đã tự khoanh phạm vi bằng 3 lựa chọn trên, và phạm vi file
  đã liệt kê đủ ở mục Nguyên văn; không còn vùng nào để hỏi "có động vào hay không".
- Bậc 7 thiếu cấu hình → user chọn **4a: nhóm B (Python/TS/JS/Lua/C/C++) CHẶN như bậc 1–4;
  nhóm A chỉ cảnh báo**.
- Kiểm hiệu ứng ở intake → user chọn **5a: agent chọn một hàm bất kỳ có sẵn trong repo, gọi
  `find_references`, đối chiếu `grep` cùng ký hiệu; ĐẠT khi LSP phủ số file ≥ grep**. Không
  neo vào file/dòng cố định.
- Script làm gì khi thiếu cấu hình → user chọn **6a: chỉ in nội dung cần tạo và xin phép**,
  giữ nguyên luật cứng "script chỉ chẩn đoán, không tự sửa".
- Câu luật mới → user chọn **7a: một câu ngắn nêu nguyên tắc chọn lớp theo loại truy vấn, trỏ
  về bảng ở file gốc**; giữ cơ chế test khớp-từng-chữ ở 5 chỗ móc.

### Lộ trình

| Bước / phase | CÓ-BỎ | Vì sao |
|---|---|---|
| research thêm | **BỎ** | 2 truy vấn đã trả lời đủ; ràng buộc còn lại là ràng buộc nội bộ repo, không có ẩn số ngoài |
| spec | **CÓ** | khung bất biến |
| diagram | **CÓ** | bắt buộc ở lane full, không bao giờ bỏ; một sơ đồ cho luồng "mở request → kiểm thang → kiểm hiệu ứng → vào việc" |
| plan | **CÓ** | khung bất biến |
| chia sub-agent | **BỎ** | phạm vi nhỏ và các phần phụ thuộc nhau (sửa câu luật → 5 chỗ móc → test); tách ra chỉ tốn công gộp |
| implement | **CÓ** | khung bất biến |
| QC bằng agent độc lập | **CÓ** | luật này tự nó là luật về "đừng tin thang báo ĐẠT"; để chính tôi tự chấm là đúng cái bẫy vừa mắc |
| deep review | **BỎ** | thay đổi là luật + 1 bậc script, không có thuật toán hay đánh đổi kiến trúc cần review riêng |
| report | **CÓ** | khung bất biến |

