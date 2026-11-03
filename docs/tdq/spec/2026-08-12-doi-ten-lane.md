# SPEC — Đổi nhãn lane: `chế độ nhanh (express)` / `chế độ chuyên sâu (deep)`

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-12 · Bản: 1.0 · Brief: ../brief/2026-08-12-doi-ten-lane.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: mọi chữ người dùng ĐỌC gọi hai lane là `chế độ nhanh (express)` và
  `chế độ chuyên sâu (deep)`; mọi chữ người dùng GÕ để duyệt/khởi tạo chấp nhận thêm bí
  danh tiếng Việt và tiếng Anh mới, trong khi máy vẫn lưu `quick`/`full` như cũ.
- Trong phạm vi: một bảng nhãn duy nhất trong `scripts/tdq_state.py`; lớp bí danh cho CLI
  và cho hai regex nhận câu duyệt; văn bản 34 file sống ở `scripts/ hooks/ skills/
  portable/ README.md .claude-plugin/`.
- NGOÀI phạm vi: đổi giá trị `lane` trong state; đổi 4 khoá `quick_*`; đổi tên file
  `quick-lane.md`; migrate state đang tồn tại; viết lại 70 tài liệu cũ trong `docs/tdq/`;
  đổi 168 dòng test đang khoá cứng chuỗi `quick`/`full`.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Tiền lệ đã có (AWS Step Functions Standard/Express); việc này thuần trong repo |
| Interview | CÓ (đã xong) | 4 câu đã chốt, ghi ở brief mục `## Hỏi đáp` |
| QC độc lập (agent) | BỎ | Bề mặt chữ + bí danh, kiểm được bằng full-suite và grep |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | `LANE_LABELS = {"quick": "chế độ nhanh (express)", "full": "chế độ chuyên sâu (deep)"}` + hàm `lane_label(lane)` | `scripts/tdq_state.py` | test mới: `lane_label("quick")` trả đúng chuỗi; `lane_label("xyz")` trả lại `"xyz"` |
| 2 | Bảng bí danh `LANE_ALIASES`: `nhanh, express, quick → quick`; `chuyen-sau, chuyensau, deep, full → full` | `scripts/tdq_state.py` | test: `init <slug> express` ghi `lane=quick`; `approve nhanh` = `approve quick` |
| 3 | CLI `init`/`approve` nhận bí danh, `USAGE` in nhãn mới | `scripts/tdq_state.py` (USAGE, `VALID_LANES`, `APPROVE_TARGETS`) | chạy `init t express` rồi đọc state thấy `lane=quick`; `--help` chứa "chế độ nhanh" |
| 4 | `PHASE_TABLE` + `render_phases_md` in nhãn mới ở chỗ mô tả lane | `scripts/tdq_state.py` | `phases-doc --plugin-root` khớp file đã regenerate (test sẵn có) |
| 5 | Regex nhận câu duyệt hiểu thêm "duyệt nhanh"/"duyệt express" | `hooks/scripts/prompt_context.py:26`, `hooks/scripts/bash_gate.py:42` | test: chuỗi `duyệt nhanh` kích hoạt đúng nhánh như `duyệt quick` |
| 6 | `APPROVE_HINTS` gợi ý câu duyệt bằng nhãn mới, vẫn nêu `quick` chạy được | `hooks/scripts/_common.py:29` | grep thấy "duyệt nhanh"; thông điệp ≤ giới hạn `trim()` |
| 7 | Văn bản 6 skill `tdq-*` gọi lane bằng nhãn mới | `skills/**` (62 dòng) | `grep -rn 'lane quick\|lane full' skills/` → 0 dòng còn cách gọi cũ trần trụi |
| 8 | Bản portable đồng bộ | `portable/**` (41 dòng) | tương tự #7 cho `portable/` |
| 9 | `README.md` + `.claude-plugin/plugin.json` mô tả dùng nhãn mới | 2 file | grep thấy "chế độ nhanh (express)" |
| 10 | Mục CHANGELOG + bump patch | `CHANGELOG.md`, `plugin.json` | `head -12 CHANGELOG.md` có mục mới |

Ba script canvas (`canvas_a4_ch4_ch7.py`, `canvas_layout_apply.py`, `claude_export.py`)
chỉ chứa chữ trong nội dung sơ đồ — cập nhật cùng #7 nếu chuỗi là chữ người đọc.

## 3. Cách tiếp cận & lý do
- Chọn: một nguồn sự thật `LANE_LABELS` cho nhãn, một `LANE_ALIASES` cho đầu vào; định
  danh nội bộ đứng yên.
- Vì: rủi ro hồi quy thấp nhất, không migrate state, không phá 168 dòng test; người dùng
  cũ gõ `duyệt quick` vẫn chạy nên không có đường gãy.
- Đã loại: đổi thẳng giá trị `lane` thành `express`/`deep` — vì phải migrate state đang
  tồn tại, sửa 4 khoá `quick_*`, 168 dòng test và 70 tài liệu lịch sử, đổi lấy đúng một
  lợi ích là "nhất quán trong file JSON không ai đọc".
- Đã loại: chỉ đổi nhãn mà KHÔNG thêm bí danh — vì dạy người dùng nói "chế độ nhanh" rồi
  không nhận câu đó là tự tạo bẫy.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build / tdq-conventions | plugin:tdq-workflow | NỀN | khung đang chạy request này |
| Đã xét 20+ skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này chỉ đổi chuỗi hiển thị và thêm bảng bí danh, không sinh runtime mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng `python3 -m pytest tests/ -q`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bí danh nuốt nhầm câu chat thường ("làm nhanh giúp tôi") | Duyệt oan — nặng nhất | Bí danh chỉ nhận khi đứng ngay sau "duyệt"; không nhận `nhanh` đứng một mình |
| Sửa `PHASE_TABLE` làm lệch `phases.md` | test đỏ | Chạy lại `phases-doc --plugin-root` ngay trong task đó |
| Thông điệp hook dài quá `trim()` (3 dòng / 200 ký tự) | Cắt mất lệnh thoát | Đếm ký tự trong test của #6 |
| Nhãn dài làm status line xấu | Khó đọc | Chỗ chật dùng phần tiếng Việt, bỏ ngoặc |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| 1 | Toàn bộ test cũ + mới | `python3 -m pytest tests/ -q` | xanh, số test ≥ 479 |
| 2 | State không đổi lược đồ | `init t express` → đọc `docs/tdq/state.json` | `lane` = `quick` |
| 3 | Câu duyệt cũ vẫn chạy | test regex với `duyệt quick` | khớp như trước |
| 4 | Câu duyệt mới chạy | test regex với `duyệt nhanh`, `duyệt express` | khớp |
| 5 | Không còn cách gọi cũ trong chữ sống | `grep -rn 'lane quick\|lane full' skills/ portable/ README.md` | 0 dòng |
| 6 | Tài liệu lịch sử nguyên vẹn | `git diff --stat docs/tdq/` | không có file cũ nào bị sửa |
| 7 | `phases.md` khớp bộ sinh | test sẵn có `test_phases_doc_regenerated` | PASS |
| 8 | Lint tài liệu | `python3 scripts/doc_lint.py CHANGELOG.md docs/tdq/spec/2026-08-12-doi-ten-lane.md` | không lỗi |
