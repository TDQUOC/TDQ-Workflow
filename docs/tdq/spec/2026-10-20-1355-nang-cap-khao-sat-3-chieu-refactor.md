# SPEC — Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor

Ngày: 2026-10-20 · Bản: 1.0 · Brief: ../brief/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi
- Mục tiêu: Khắc phục triệt để lỗi tra cứu code thiếu và phân tích sai lệch chủ đích khi refactor/bổ sung tính năng bằng cách: gỡ bỏ hard deny đếm lượt Grep trong phase khảo sát (`analyze`/`quick_analyze`), bắt buộc đối chiếu tam giác 3 nguồn (Grep + LSP + Graphify) trước khi chốt phương án, bổ sung ngoại lệ Clean Architecture cho Rung 1 khi người dùng yêu cầu Refactor, và chuẩn hóa bảng Trước vs Sau trong Spec/Plan.
- Trong phạm vi:
  - Cập nhật `hooks/scripts/search_gate.py` & `scripts/search_rules.py`: Cho phép Grep tự do không giới hạn quota trong phase `analyze`, `quick_analyze` và `no_state`; duy trì cổng 3 tầng chuẩn trong phase `implement`.
  - Cập nhật `skills/tdq-intake/SKILL.md`, `references/analyze-full.md`, `references/quick-lane.md`: Quy định quy trình Khảo sát Code 3 Chiều (Grep quét rộng -> LSP đào sâu cấu trúc -> Graphify kiểm tra vỡ lan) và bảng đối chiếu vùng chạm bắt buộc.
  - Cập nhật `skills/tdq-build/references/rules/chung.md`: Bổ sung ngoại lệ Refactor & Mở rộng kiến trúc vào mục `### Never simplify these away` của Rung 1 (tôn trọng thiết kế của người dùng, không ép biến thành hàm phẳng 1 dòng).
  - Cập nhật `skills/tdq-spec/references/spec-template.md` (§3) và `skills/tdq-plan/references/plan-template.md`: Bắt buộc khối so sánh Hiện trạng (Trước) vs Thiết kế mới (Sau) khi bổ sung hoặc refactor.
  - Cập nhật `scripts/tdq_setup.py`: Đồng bộ nguyên tắc khảo sát 3 chiều và ngoại lệ refactor vào `KHOI_HUONG_DAN` (`CLAUDE.md`).
  - Viết test suite kiểm chứng độc lập hành vi của gate tìm kiếm và các quy tắc mới.
- NGOÀI phạm vi:
  - Không gỡ bỏ cổng tìm kiếm trong phase `implement` (vẫn duy trì kỷ luật gọi LSP trước khi grep khi viết mã).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Yêu cầu nằm trọn trong kiến trúc nội bộ của TDQ Workflow |
| Interview | BỎ | Yêu cầu và phương án kỹ thuật đã được làm rõ chi tiết |
| QC độc lập (agent) | CÓ | Chạy toàn bộ unit test kiểm chứng logic phân loại và gate tìm kiếm |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Gate tìm kiếm mở khóa phase analyze | `hooks/scripts/search_gate.py`, `scripts/search_rules.py` | Phase analyze cho phép grep tự do không bị deny hoặc cạn quota |
| 2 | Quy trình khảo sát code 3 chiều | `skills/tdq-intake/SKILL.md`, `references/analyze-full.md` | Tài liệu quy định rõ 3 bước: Grep rộng -> LSP sâu -> Graphify vỡ lan |
| 3 | Ngoại lệ Refactor cho Rung 1 | `skills/tdq-build/references/rules/chung.md` | Rung 1 bảo toàn Clean Architecture/SOLID khi có yêu cầu Refactor |
| 4 | Khối Hiện trạng Trước vs Sau | `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md` | Bảng Trước vs Sau bắt buộc trong spec §3 và plan |
| 5 | Đồng bộ instruction toàn cục | `scripts/tdq_setup.py` | `KHOI_HUONG_DAN` và `CLAUDE.md` ghi nhận quy tắc khảo sát 3 chiều |
| 6 | Bộ kiểm thử tự động | Bộ test suite của repo | Toàn bộ unit tests kiểm tra gate tìm kiếm và quy tắc mới đều PASS |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `search-gate-enhance` | `hooks/scripts/search_gate.py`, `scripts/search_rules.py` | không | 1 |
| `intake-triangulation` | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-intake/references/quick-lane.md` | `search-gate-enhance` | 2 |
| `rules-refactor-intent` | `skills/tdq-build/references/rules/chung.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md` | không | 3, 4 |
| `instruction-sync` | `scripts/tdq_setup.py` | `intake-triangulation`, `rules-refactor-intent` | 5 |

## 3. Cách tiếp cận & lý do
- Chọn:
  - Thay vì bóp nghẹt số lần Grep bằng cơ chế đếm lượt hạn hẹp (gây tâm lý co cụm sợ grep dẫn đến tra code thiếu), ta mở khóa hoàn toàn Grep trong phase khảo sát (`analyze`/`quick_analyze`).
  - Đảm bảo chất lượng bằng việc bắt buộc hoàn tất "Tam giác khảo sát": Phải kết hợp Grep quét diện rộng (tìm từ khóa, route, config), LSP đào sâu cấu trúc (tìm caller/callee gián tiếp), và Graphify kiểm tra vỡ lan (affected 2 bước nhảy).
  - Tôn trọng chủ đích tái cấu trúc của người dùng: Thêm ngoại lệ rõ ràng vào Rung 1 của luật tinh gọn, không cho phép Agent tự ý bẻ lái yêu cầu refactor của người dùng thành sửa tối thiểu 1 dòng nếu điều đó phá vỡ cấu trúc sạch.
- Vì: Giải quyết triệt để 2 vấn đề nhức nhối được phản ánh: (1) tra code thiếu do sợ bị khóa grep, và (2) phân tích sai lệch chủ đích do luật tinh gọn bị áp dụng máy móc.
- Đã loại:
  - Loại bỏ phương án tắt hoàn toàn search_gate ở mọi phase: Vì trong phase `implement`, việc ép gọi LSP trước khi grep vẫn rất cần thiết để giữ kỷ luật viết mã TDD và tra cứu symbol chính xác.

## 3b. Năng lực & công cụ

Phân vân → DÙNG. Kiểm kê ngày 2026-10-20: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-setup | plugin:tdq-workflow | NỀN | Cập nhật `KHOI_HUONG_DAN` ghim điều luật khảo sát 3 chiều vào `CLAUDE.md` |
| tdq-intake | plugin:tdq-workflow | NỀN | Chuẩn hóa quy trình khảo sát 3 chiều trong `analyze-full.md` |
| tdq-build | plugin:tdq-workflow | NỀN | Bổ sung ngoại lệ Refactor cho Rung 1 trong `chung.md` và thực thi TDD |
| tdq-spec | plugin:tdq-workflow | NỀN | Cập nhật khối Trước vs Sau trong `spec-template.md` |
| tdq-plan | plugin:tdq-workflow | NỀN | Cập nhật template plan bảng đối chiếu vùng chạm |
| Đã xét 20 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config (`TDQ_LOG=0`).
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID và clean code invariants trong `skills/tdq-conventions/references/clean-code.md`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ:
- `hooks/scripts/search_gate.py`: Tiếp tục thực thi không subprocess, thời gian phản hồi < 5ms, fail-safe (nếu có lỗi không làm crash tool call).
- Trong phase `implement`, hàng rào 3 tầng (LSP trước, Grep sau) vẫn hoạt động nguyên vẹn để bảo vệ kỷ luật viết mã.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Mở khóa Grep trong analyze khiến Agent lười gọi LSP | Thiếu thông tin kiểu dữ liệu và caller gián tiếp | Bắt buộc đối chiếu tam giác 3 nguồn trong tài liệu và template trước khi rời phase analyze |
| Nới lỏng Rung 1 khiến Agent viết code over-engineering | Tăng nợ kỹ thuật không cần thiết | Ngoại lệ chỉ áp dụng khi prompt/brief có từ khóa Refactor, Tái cấu trúc, Clean Architecture hoặc Mở rộng |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Gate tìm kiếm mở khóa trong Analyze | Khi phase là `analyze`/`quick_analyze`, các lệnh grep được cho phép không bị deny | Baseline bị chặn deny nếu chưa gọi LSP | Kiểm tra cờ phase trong search_gate |
| Q2 | Hàng rào Implement giữ nguyên | Khi phase là `implement`, search_gate vẫn duy trì quy tắc 3 tầng chuẩn | Baseline đang hoạt động chuẩn ở implement | Giữ nguyên logic nhánh implement |
| Q3 | Ngoại lệ Refactor cho Rung 1 | `chung.md` chứa ngoại lệ bảo toàn Clean Architecture/SOLID khi người dùng yêu cầu Refactor | Baseline chưa có ngoại lệ này | Định nghĩa rõ điều kiện ngoại lệ |
| Q4 | Bảng Hiện trạng Trước vs Sau & Đồng bộ | `spec-template.md`, `plan-template.md`, `CLAUDE.md` có khối so sánh Trước vs Sau và bảng 3 chiều | Baseline chỉ có bảng đối chiếu cơ bản | Cập nhật mẫu chuẩn vào các file template |

DoD: `search_gate.py` cho phép grep tự do trong phase analyze nhưng giữ chuẩn trong implement; quy trình khảo sát 3 chiều và ngoại lệ refactor cho Rung 1 được chuẩn hóa trong tài liệu; bảng Trước vs Sau tích hợp đầy đủ; toàn bộ test suite liên quan PASS 100%.

## 7. Câu hỏi còn mở
(Không có. Toàn bộ phạm vi kỹ thuật đã được làm rõ.)
