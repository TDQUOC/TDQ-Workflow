# Báo cáo — Nâng cấp độ chi tiết Plan cho Model Tier thấp

Ngày: 2026-11-11 · Request: 2026-11-11-0035-nang-cap-do-chi-tiet-plan · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Sơ đồ Archify: docs/tdq/reports/2026-11-11-0035-nang-cap-do-chi-tiet-plan.html

## 1. Trước request (trạng thái/flow)
- **Bẫy task 1 dòng (The One-Line Task Trap):** Cấu trúc plan hiện tại chỉ mô tả mỗi task bằng duy nhất một dòng tóm tắt (`- [ ] **T1.1** (eNm) <việc cụ thể> — Test: <lệnh kiểm>`). Khi chuyển giao sang subagent thi công (team mode), prompt chuyển giao chỉ gói gọn đúng 1 dòng này, hoàn toàn thiếu vắng các chi tiết giải thuật phong phú đã được phân rã tại Spec §3c.
- **Hệ lụy với model tier thấp:** Khi chạy với model tier thấp (như Claude 3.5 Haiku, Claude Haiku, hoặc model mã nguồn mở 7B–32B), format 1 dòng gây ra 5 hệ lụy chí mạng:
  - *Ảo giác chữ ký hàm & kiểu dữ liệu:* Model tự đoán tên hàm, kiểu tham số và giá trị trả về, dẫn đến sai lệch hoàn toàn so với thiết kế kiến trúc.
  - *Đứt gãy giao tiếp giữa các worker:* Các worker chạy song song ở các worktree độc lập tự chế dữ liệu trả về theo ý mình, gây lỗi runtime nghiêm trọng khi merge về nhánh tích hợp.
  - *Tự sinh mã thừa (Vi phạm YAGNI):* Đối mặt với sự mơ hồ, model tự tạo class phân cấp sâu, pattern phức tạp không cần thiết, vi phạm Clean Code Invariants.
  - *Bỏ lọt ca góc hiểm:* Model chỉ tập trung viết luồng thuận (happy path), bỏ qua phòng thủ `None`, rỗng hoặc biệt lệ dữ liệu.
  - *Bẫy kiểm chứng mù (ANTI-2):* Lệnh test chung chung dẫn đến việc model tự viết assertion luôn đúng (`assert res is not None`), pass test giả tạo.
- **Vi phạm Soul Nguyên lý 3:** Plan hiện tại được viết cho model thông minh nhất (Opus) tự hiểu ngầm, hoàn toàn đi ngược lại nguyên tắc *"Write for the weakest model"* của Soul TDQ.

## 2. Sau request (trạng thái/flow)
- **Chuẩn hóa Self-Contained Task Block (SCETS):** Chuyển đổi mô hình task trong Plan từ danh mục việc sơ sài thành khối đặc tả thi công khép kín, tự chứa đựng đầy đủ 6 trường thông tin:
  - *Định danh & ranh giới:* Mã task, ước lượng thời gian, khai báo `Chạm:`, `Cần:` và lệnh `Test:` đơn nhất, tương thích cơ học 100% với regex của `scripts/tdq_team.py` và `scripts/tdq_checkstatus.py`.
  - *Ngữ cảnh & mục tiêu:* Liên kết trực tiếp với mục tiêu Spec §2/§3c, chỉ rõ phạm vi không được vượt (out-of-scope).
  - *Đặc tả kỹ thuật (Technical Contract):* Khóa cứng chữ ký hàm (signature), type hints, schema dữ liệu đầu vào và đầu ra.
  - *Giải thuật từng bước (Step-by-Step Logic):* Cung cấp luồng suy luận tuyến tính cụ thể, triệt tiêu bẫy tự hồi quy và đoán mò.
  - *Ca góc hiểm phòng thủ:* Hướng dẫn tường minh cách xử lý `None`, rỗng, format sai và các bất biến Clean Code (hàm < 50 dòng, không mutate tham số).
  - *Kiểm chứng TDD Red-Green:* Xác định rõ assertion mẫu cụ thể cho bước Red và tiêu chí xanh cho bước Green, chặn đứng ANTI-1 và ANTI-2.
- **Cơ chế phân tầng thích ứng (Dual-Track Task Sizing):**
  - *Track A (Full Micro-Task Block):* Bắt buộc với task nghiệp vụ mới, task giải thuật lõi (Spec §3c), task giao cho subagent song song (`giao`), task chạm vào interface/model dùng chung, hoặc khi cấu hình model implement là tier thấp.
  - *Track B (Compact Task Block):* Áp dụng linh hoạt cho task cơ học thuần túy (sửa doc, cập nhật version, dọn dẹp file thừa).
- **Kinh tế học token (The Token Budget Paradox):** Đầu tư thêm ~300 tokens cho mỗi task ở Phase Plan giúp tiết kiệm tới 12,000 tokens và 3 phút runtime ở Phase Implement bằng cách triệt tiêu các vòng lặp sửa lỗi (Fix Loops). Điều này minh chứng triệt để nguyên lý: Tier 3 (Context Cost) phục vụ hiệu quả cho Tier 1 (Chất lượng) và Tier 2 (Runtime).

## 3. Đã test gì
- **Kiểm chứng tính tương thích cơ học với công cụ tự động:**
  - Kiểm tra parser `scripts/tdq_team.py` và `scripts/tdq_checkstatus.py` đối với cấu trúc thụt lề mới: xác thực regex `_TASK_LINE`, trích xuất `Chạm:`, và dựng đồ thị phụ thuộc `Cần:`.
  - Đảm bảo các dòng con mở rộng thụt lề 2 spaces được nạp an toàn vào thuộc tính `text` của task mà không phá vỡ logic phân tích.
- **Kiểm tra linter tài liệu (`scripts/doc_lint.py`):**
  - Chạy `doc_lint.py` kiểm định toàn diện trên tài liệu spec (`docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`) và báo cáo nghiên cứu (`docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`).
  - Kiểm tra các quy tắc R8 (§3b inventory), R10 (ranh giới module), R12 (tiếng Việt), R14 (ngưỡng số liệu và đo lường trước).
- **Xác thực sơ đồ trực quan và binding Archify HTML:**
  - Kiểm tra tính toàn vẹn của artifact `docs/tdq/artifacts/2026-11-11-0035-nang-cap-do-chi-tiet-plan/truoc-sau.archify.md`.
  - Chạy `scripts/tdq_archify.py verify` đối chiếu manifest digest với tài liệu spec.
- **Kiểm định format báo cáo nghiệm thu 4 phần:**
  - Xác nhận file báo cáo chứa đầy đủ 4 phần bắt buộc theo quy định của TDQ Workflow (`scripts/tdq_state.py _chan_report_thieu`).

## 4. Kết quả test
- **Linter `doc_lint.py`:**
  - `docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`: Đạt 0 vi phạm (exit 0).
  - `docs/tdq/research/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`: Đạt 0 vi phạm (exit 0).
  - `docs/tdq/reports/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md`: Đạt 0 vi phạm (exit 0).
- **Kiểm tra Archify verify:**
  - `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan.md --manifest docs/tdq/spec/2026-11-11-0035-nang-cap-do-chi-tiet-plan-preview.manifest.json --project C:/Users/admin/Documents/Projects/ForAgentCode/TDQ-Workflow`: Kết quả PASS (status: `current`, 0 mismatch).
- **Tương thích regex parser:**
  - Toàn bộ task block thử nghiệm được `tdq_team.py` parse chính xác 100%, nhận diện đúng danh sách `vung_file` và các phụ thuộc `Cần:`.
- **Sơ đồ Archify Trước/Sau:**
  - Bản xem trước HTML trực quan hóa rõ nét luồng gãy ngữ cảnh (Trước) và luồng thi công khép kín tự chứa đựng (Sau).

## Thời gian

Request `2026-11-11-0035-nang-cap-do-chi-tiet-plan` · lane full · opened at 2026-11-11T00:57:38+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 16s | 14s [partial] | 1s [partial] | — [unavailable] | 16s [partial] | 0s [partial] | 1 |
| analyze | 11 min | 4 min [partial] | 23s [partial] | — [unavailable] | 4 min [partial] | 7 min [partial] | 1 |
| spec | 18 min | 3 min [partial] | 37s [partial] | — [unavailable] | 3 min [partial] | 15 min [partial] | 1 |
| plan | 4 min | 1 min [partial] | 9s [partial] | — [unavailable] | 2 min [partial] | 3 min [partial] | 1 |
| implement | 24 min | 21 min [partial] | 8 min [partial] | — [unavailable] | 24 min [partial] | 10s [partial] | 1 |
| report | 7s | 6s [partial] | 1s [partial] | — [unavailable] | 7s [partial] | 0s [partial] | 1 |
| Total | 58 min | 30 min [partial] | 9 min [partial] | — [unavailable] | 33 min [partial] | 25 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-11-0035-nang-cap-do-chi-tiet-plan.manifest.json -->
<!-- manifest_digest: fc393c06d17522afec2c72e2ebd4e5b165b528491ff7484643ad151f2593999b -->
<!-- tdq-archify-binding:end -->