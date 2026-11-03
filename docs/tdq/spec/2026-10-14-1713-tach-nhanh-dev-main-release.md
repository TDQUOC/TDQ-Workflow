# SPEC — Tách nhánh dev để phát triển và nhánh main để phát hành sạch

Ngày: 2026-10-14 · Bản: 1.0 · Brief: ../brief/2026-10-14-1713-tach-nhanh-dev-main-release.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

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

- **Mục tiêu**: Tách quy trình Git của dự án TDQ-Workflow thành 2 nhánh chính: nhánh `dev` làm nhánh phát triển mặc định (lưu giữ đầy đủ `docs/`, `tests/`, `evals/`, `graphify-out/` và toàn bộ công cụ nội bộ) và nhánh `main` làm nhánh phát hành (release) gọn sạch chỉ chứa phần lõi runtime của plugin (~136 files, giảm hơn 90% số lượng file so với nhánh `dev`), đồng thời cung cấp lệnh CLI tự động xuất bản từ `dev` sang `main` bằng Git plumbing mà không gây xung đột merge `modify/delete`.
- **Trong phạm vi**:
  1. Mở rộng `scripts/build_portable.py` với chế độ phát hành nhánh `main` sạch (`--sinh-main`, kèm các tùy chọn `--nguon`, `--nhanh-dich`, `--dry-run`):
     - Định nghĩa tập quy tắc lọc cho nhánh release (`RELEASE_EXCLUDE_DIRS`, `RELEASE_EXCLUDE_FILES`, `RELEASE_EXCLUDE_SCRIPTS`): loại bỏ các thư mục cấp gốc `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, các file cấp gốc `CHANGELOG-archive.md`, `pyrightconfig.json`, thư mục `scripts/samples/` và 12 script thuần dev/canvas/audit trong `scripts/` (`canvas_a4_ch4_ch7.py`, `canvas_a4_rebuild.py`, `canvas_draw.py`, `canvas_layout_apply.py`, `canvas_move_block.py`, `check_canvas_layout.py`, `doc_dup.py`, `doc_index.py`, `i18n_check.py`, `luat_phan_loai.py`, `skill_router.py`, `tdq_eval.py`).
     - Giữ nguyên toàn bộ 35 script runtime trong `scripts/`, toàn bộ `skills/`, `agents/`, `hooks/`, `portable_src/`, `claude-export/`, các thư mục adapter host (`.claude-plugin/`, `.codex-plugin/`, `.opencode/`, `.agents/`, `.claude/`, `.codex/`) và các file gốc (`README.md`, `CHANGELOG.md`, `.gitignore`, `.gitattributes`, `.graphifyignore`, `.env.example`).
     - Sử dụng Git plumbing (`git ls-tree -r -z`, `git update-index -z --index-info` trên `GIT_INDEX_FILE` tạm, `git write-tree`, `git commit-tree`, `git update-ref`) để tạo commit release sạch trên nhánh đích (`main`) nối tiếp parent của `main` hiện tại với thông điệp `release: v<version> (from <nguon>@<short_sha>)`, không gắn parent vào nhánh `dev` và không chạm vào working tree hiện hành. Nếu cây thư mục sau khi lọc không đổi so với `main` hiện tại thì bỏ qua tạo commit mới (idempotent).
  2. Cập nhật `scripts/tdq_test.py` để khi `docs/tdq/state.json` không khai `nhanh_goc`, công cụ tự động kiểm tra sự tồn tại của nhánh `dev` (`refs/heads/dev`) trong repo và ưu tiên so diff với `dev` trước khi fallback về `main`.
  3. Cập nhật `skills/tdq-intake/references/nhanh-request.md` và `docs/kien-truc.md` để ghi nhận quy ước nhánh phát triển `dev` và lệnh xuất bản sang nhánh `main`, đồng bộ `docs/tdq/token-budget.json`.
  4. Xây dựng bộ unit test đầy đủ cho cơ chế lọc đường dẫn release, tạo commit snapshot `--sinh-main` (cả `--dry-run` và idempotent) và tự động nhận diện nhánh gốc `dev` trong `tdq_test.py`.
  5. Khi hoàn tất và gộp kết quả request này: khởi tạo nhánh `dev` chứa đầy đủ toàn bộ lịch sử/tài liệu/test phát triển và chạy lệnh xuất bản nhánh `main` sạch.
- **NGOÀI phạm vi**:
  - Không thay đổi cấu trúc hoặc hành vi đóng gói của 3 bundle portable (`--sinh-agy`, `--sinh-hook-claude`, `--dest`) hiện có trong `scripts/build_portable.py`.
  - Không xóa bất kỳ file nào thuộc `docs/`, `tests/` hay script nội bộ trên nhánh `dev`.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Bài toán sử dụng Git plumbing chuẩn (`ls-tree`, `update-index`, `write-tree`, `commit-tree`, `update-ref`) và kiến trúc sẵn có trong repo |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 5 câu hỏi (`1a 2A 3A 4A 5A`) |
| QC độc lập (agent) | BỎ | Người dùng đã chọn mức QC tiêu chuẩn (`muc_qc=full` ở câu 4A), không gọi sub-agent `tdq-qc-tester` |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Chế độ phát hành nhánh `main` sạch (`--sinh-main`) và bộ lọc đường dẫn release | `scripts/build_portable.py` | Hàm `la_duong_dan_release`, `loc_muc_ls_tree`, `sinh_nhanh_main` và cờ CLI `--sinh-main [--nguon] [--nhanh-dich] [--dry-run]` tạo đúng commit snapshot sạch trên nhánh đích, giữ nguyên working tree hiện tại và ghi log chuẩn |
| 2 | Cơ chế tự nhận diện nhánh gốc `dev` khi chạy test vùng chạm | `scripts/tdq_test.py` | Hàm `nhanh_goc_mac_dinh(repo)` trả về `"dev"` khi repo có `refs/heads/dev`, fallback về `"main"` khi không có `refs/heads/dev` |
| 3 | Tài liệu quy ước mô hình 2 nhánh `dev` (develop) và `main` (release) | `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json` | Mô tả rõ vai trò nhánh `dev` và lệnh xuất bản sang `main`; đạt `doc_lint.py`, `i18n_check.py` và khóa `token_budget.py` |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP (`scripts/build_portable.py` và `scripts/tdq_test.py` là 2 module CLI độc lập không import lẫn nhau; tài liệu quy ước nằm ở tầng `skills/` và `docs/`):

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `release-main` | `scripts/build_portable.py` | Không | 1 |
| `base-branch-detect` | `scripts/tdq_test.py` | Không | 2 |
| `branch-docs` | `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json` | `release-main` (nhắc tên lệnh `build_portable.py --sinh-main`) | 3 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. **Mở rộng `scripts/build_portable.py` thay vì tạo file script mới (Rung 2 của bậc thang `TDQ:GON`)**:
     - `scripts/build_portable.py` đã là nơi quản lý danh sách loại trừ (`EXCLUDE_DIRS`, `EXCLUDE_FILES`), đọc phiên bản plugin (`plugin_version`) và có sẵn dịch vụ log (`log`). Đặt chức năng `--sinh-main` tại đây giúp tránh đẻ thêm file mới trong `scripts/`.
  2. **Sử dụng Git Plumbing trên Index tạm (`GIT_INDEX_FILE`) để tạo commit release trên `main`**:
     - Đọc danh sách tracked files của nhánh nguồn (`dev`) bằng `git ls-tree -r -z <nguon_sha>`.
     - Lọc các dòng qua `la_duong_dan_release(path)` để loại bỏ toàn bộ `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, `CHANGELOG-archive.md`, `pyrightconfig.json`, `scripts/samples/` và 12 script thuần dev/canvas/audit.
     - Ghi danh sách đã lọc vào một file index tạm thông qua `git update-index -z --index-info`, sau đó gọi `git write-tree` để thu được `tree_sha` sạch.
     - Tạo commit mới bằng `git commit-tree <tree_sha> -p <main_sha> -m "release: v<version> (from <nguon>@<short_sha>)"` và cập nhật ref bằng `git update-ref refs/heads/<nhanh_dich> <commit_sha>`.
- **Vì**:
  - Thao tác qua `GIT_INDEX_FILE` tạm và `git commit-tree` hoàn toàn không cần `git checkout main`, không bao giờ làm bẩn hay đụng chạm tới working tree đang làm việc trên `dev`, thực thi trong `< 1 giây`.
  - Commit trên `main` chỉ có 1 parent là `main` cũ (không gắn parent thứ 2 vào `dev`), nên các thay đổi liên tục trong `docs/` và `tests/` trên `dev` không bao giờ gây xung đột merge `modify/delete` ở các lần release tiếp theo, đồng thời vẫn đảm bảo `git push origin main` là fast-forward.
- **Đã loại**:
  - *Phương án dùng `git checkout main && git merge dev && git rm -r docs tests ...`* — loại vì làm thay đổi working tree hiện tại và từ lần release thứ 2 trở đi Git sẽ báo conflict `modify/delete` trên mọi file `docs/` và `tests/` được sửa ở `dev`.
  - *Phương án tạo file script mới `scripts/tdq_release.py`* — loại ở Rung 2 của `TDQ:GON` vì `scripts/build_portable.py` đã đảm nhiệm vai trò xuất bản phân phối của repo.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | tiếp nhận, phân tích yêu cầu và phỏng vấn chốt phạm vi |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật và kiểm tra R8, R11, R14 |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch triển khai theo từng task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD đỏ -> xanh, chạy QC mức `full` và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng và hợp đồng tài liệu |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái |
| tdq-lean | plugin:tdq-workflow | NỀN | áp dụng bậc thang build-less-than-asked (`TDQ:GON`) |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra môi trường công cụ và LSP |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi cần |
| Đã xét 12 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Chế độ `--sinh-main` trong `scripts/build_portable.py` và hàm nhận diện nhánh gốc trong `scripts/tdq_test.py` ghi log kèm ISO timestamp ra `stderr` (hiển thị rõ nhánh nguồn, nhánh đích, số lượng file giữ lại/loại bỏ, `tree_sha` và `commit_sha`), tắt được qua biến môi trường `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**: Mọi thao tác tạo tree và commit đều chạy thật qua Git plumbing trên kho Git.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**: Tuân thủ quy trình TDD đỏ → xanh nghiêm ngặt.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill — việc này chạm ở `skills/tdq-intake/references/nhanh-request.md`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định (không bảng tra i18n); tài liệu sinh cho user và lời thoại viết theo `doc_lang` — việc này chạm ở `scripts/build_portable.py`, `scripts/tdq_test.py` và `skills/tdq-intake/references/nhanh-request.md`.
- 2026-10-03 (yêu cầu 1907): **trọn bộ test chỉ chạy ở 2 cổng.** Giữa các bước, `scripts/tdq_test.py vung-cham` chạy vùng chạm cộng bán kính do máy tính — việc này chạm ở `scripts/tdq_test.py` (hàm `nhanh_goc_mac_dinh`).

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Lọc nhầm một script trong `scripts/` mà runtime `skills/` hoặc `hooks/` có import bắc cầu | Plugin trên nhánh `main` bị lỗi `ModuleNotFoundError` khi chạy | Đã phân tích bao đóng bắc cầu AST trên toàn bộ 48 file trong `scripts/`: giữ nguyên đủ 35 script thuộc bao đóng runtime và viết unit test kiểm tra không có script giữ lại nào import script nằm trong `RELEASE_EXCLUDE_SCRIPTS` |
| Khi đang làm việc trên `dev` mà `state.json` rỗng (`phase=idle`), chạy `tdq_test.py vung-cham` so diff nhầm với `main` (vốn đã bỏ `tests/`) | `git diff main...HEAD` liệt kê toàn bộ 1,336 file đã lọc khỏi `main`, làm `vung-cham` luôn rơi về chạy trọn bộ suite | Cập nhật `nhanh_goc_mac_dinh(repo)` trong `scripts/tdq_test.py` tự động chọn `"dev"` khi `refs/heads/dev` tồn tại trong repo |
| Thao tác tạo bản release làm thay đổi `.git/index` hoặc working tree đang dở dang trên `dev` | Làm hỏng trạng thái staging của lập trình viên | Thực hiện `git update-index` và `git write-tree` hoàn toàn trên biến môi trường `GIT_INDEX_FILE` trỏ tới file tạm trong `tempfile.TemporaryDirectory()` |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Bộ lọc đường dẫn release bảo toàn trọn vẹn bao đóng runtime và loại bỏ triệt để file dev/test | Trên cây Git của repo, bộ lọc loại bỏ toàn bộ `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, `CHANGELOG-archive.md`, `pyrightconfig.json`, `scripts/samples/` và 12 script dev-only; giữ lại đúng 35 script runtime (≤ 150 files tổng cộng trên nhánh release) và mọi lệnh `import` nội bộ giữa các script giữ lại đều hợp lệ | Đã đo bằng AST và `git ls-files`: cây hiện tại có 1,472 files, sau khi lọc còn 136 files (biên 14 files dưới ngưỡng 150 files) và 35/35 script runtime khép kín 100% | Nếu phát hiện thêm script phụ thuộc bắc cầu mới thì tự động giữ lại theo đồ thị AST import của `scripts/` |
| Q2 | Lệnh CLI `build_portable.py --sinh-main` hoạt động chuẩn xác, idempotent và không chạm working tree | Chạy `--sinh-main` trên repo Git tạo commit mới trên nhánh đích (`main`) chỉ chứa các file đã lọc sạch, thông điệp commit ghi rõ `from <nguon>@<sha>`, chạy lần 2 liên tiếp khi nguồn không đổi thì báo không đổi (0 commit dư), hỗ trợ `--dry-run` và giữ nguyên working tree hiện tại | Đo thử `git ls-tree` + `update-index` + `write-tree` trên 136 files mất ~0.12 giây (< 2 giây) | Nếu `git update-index --index-info` gặp đường dẫn chứa ký tự đặc biệt thì dùng cờ `-z` (NUL-delimited) chuẩn của Git plumbing |
| Q3 | Tự động nhận diện nhánh gốc `dev` trong `scripts/tdq_test.py` | Khi repo có nhánh `dev` và `state.json` không khai `nhanh_goc`, `nhanh_goc_mac_dinh` trả về `"dev"`; khi repo chỉ có nhánh `main` thì trả về `"main"` | Đã kiểm tra trên 177 test module hiện có: 0 module nào bị ảnh hưởng khi repo tạm trong test chỉ khởi tạo nhánh `main` | Kiểm tra sự tồn tại của `refs/heads/dev` bằng `git show-ref --verify --quiet refs/heads/dev` trước khi chọn `"dev"` |
| Q4 | Tài liệu quy ước nhánh, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token | Các file `skills/tdq-intake/references/nhanh-request.md`, `docs/kien-truc.md` và mã nguồn mới đạt 0 vi phạm khi chạy công cụ kiểm tra tài liệu, kiểm tra i18n và khóa ngân sách token (mọi file reference ≤ 3500 tokens) | `nhanh-request.md` hiện chỉ có 48 dòng (~360 tokens, biên > 3,000 tokens so với trần 3,500 tokens) | Giữ phần bổ sung trong `nhanh-request.md` ngắn gọn ≤ 15 dòng và chạy lại `token_budget.py` |

**DoD**:
1. `scripts/build_portable.py --sinh-main` và `scripts/tdq_test.py` hoạt động hoàn chỉnh, đạt chuẩn SOLID & độ phức tạp hàm (cyclomatic ≤ 10, cognitive ≤ 15), có đầy đủ unit test xanh 100%.
2. Nhánh release tạo ra từ `--sinh-main` không chứa `docs/`, `tests/` hay bất kỳ file dev dư thừa nào, trong khi toàn bộ 35 script runtime và cấu hình plugin đa host được bảo toàn nguyên vẹn.
3. Tài liệu `nhanh-request.md` và `docs/kien-truc.md` được cập nhật đầy đủ, đạt `doc_lint.py`, `i18n_check.py`, `token_budget.py --kiem` và vượt qua toàn bộ các bước kiểm định QC mức `full` (`QC-F1`..`QC-F4`).

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt.)
