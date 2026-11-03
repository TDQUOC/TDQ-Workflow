# SPEC — Trình bày thân thiện ở mọi chỗ giao tiếp với user

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-trinh-bay-than-thien-duyet.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: mọi khối chat TDQ hỏi user đều theo một khuôn dễ đọc, có câu dẫn xưng "bạn",
  đường dẫn file đầy đủ và lời mời trả lời nằm trong khối riêng nổi bật. Tách bước chọn
  mode thực thi thành một phase riêng sau khi plan được duyệt.
- Trong phạm vi: 7 chỗ giao tiếp (chọn pipeline, interview, cổng spec, cổng plan, cổng
  mode, cổng chế độ nhanh, câu hỏi commit) · phase `mode` mới · `APPROVE_HINTS` ·
  tài liệu tự sinh và bản `portable/` · mẫu CLAUDE.md.
- NGOÀI phạm vi: đổi điều kiện chặn của hook, đổi lược đồ state ngoài trường phase mới,
  đổi luật tick checkbox, đổi nội dung spec/plan (chỉ đổi cách TRÌNH BÀY).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, không có ẩn số thư viện/API bên ngoài. |
| Interview | XONG | 2 vòng, đã hết câu hỏi làm đổi kết quả. |
| Spec + plan | CÓ | Khung bất biến. |
| Implement | CÓ | Đụng `PHASE_TABLE`, hook, nhiều file skill và tài liệu tự sinh. |
| QC theo DoD | CÓ | Có sửa hằng máy đọc nên phải chạy full suite. |
| QC độc lập (agent) | BỎ | DoD kiểm hết bằng lệnh, không có vùng mờ cần người kiểm riêng. |
| Chia subagent | BỎ | Task đụng chung `tdq_state.py`, `_common.py`, phụ thuộc chặt. |
| Report | CÓ | Khung bất biến. |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Khuôn khối user-facing dùng chung | `skills/tdq-conventions/references/user-facing-block.md` | File tồn tại, nêu đủ 5 thành phần khuôn, `doc_lint` exit 0 |
| 2 | Luật áp khuôn cho mọi chỗ giao tiếp | `skills/tdq-conventions/SKILL.md` §1 | Có luật trỏ file khuôn, liệt kê đủ 7 chỗ, file ≤ 120 dòng |
| 3 | Phase `mode` trong bảng phase | `scripts/tdq_state.py` `PHASE_TABLE` | `tdq_state.py next` ở trạng thái plan đã duyệt mà chưa có mode in ra phase `mode` |
| 4 | `approve plan` không cần `--mode` | `scripts/tdq_state.py` | Chạy `approve plan --by "x"` exit 0, `plan_approved=true`, `implement_mode` rỗng |
| 5 | Gợi ý duyệt mới | `hooks/scripts/_common.py` `APPROVE_HINTS` | Khoá `plan` không còn chữ `mode`, có khoá `mode` mới |
| 6 | Khối trình spec/plan/mode viết lại | `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md` | Mỗi file có câu dẫn "bạn" + đường dẫn file + khối duyệt tách riêng |
| 7 | Cổng chế độ nhanh và câu hỏi commit theo khuôn | `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-build/SKILL.md` | Hai chỗ này dùng đúng khuôn ở đầu ra 1 |
| 8 | Giải thích 2 mode ở cổng mode | `skills/tdq-plan/SKILL.md` | Khối hỏi mode có 1 dòng nghĩa cho `main` và 1 dòng cho `subagent` |
| 9 | Tài liệu tự sinh + portable đồng bộ | `references/phases.md` (2 bản), `portable/workflow/*` | `pytest tests/test_phase_table.py` exit 0 |
| 10 | Mẫu CLAUDE.md khớp luồng mới | `docs/claude-md-mau.md` | Không còn câu "duyệt plan kèm mode → build ngay turn đó" |
| 11 | Test cho luồng và khuôn mới | `tests/` | `pytest tests/ -q` exit 0 |

## 3. Cách tiếp cận & lý do

- Chọn: một file khuôn duy nhất trong `tdq-conventions`, mọi skill trỏ về; phase `mode`
  là phase THẬT trong `PHASE_TABLE`.
- Vì: `PHASE_TABLE` là nguồn sự thật của hook và status line. Làm phase thật thì máy phân
  biệt được "đang chờ duyệt plan" với "đang chờ chọn mode", `next` chỉ đúng việc, và
  không ai sửa code lọt khi mode chưa chốt. Khuôn một chỗ tránh 7 bản sao trôi lệch nhau.
- Đã loại: giữ bước hỏi mode nằm trong phase `plan` — user đã chốt phương án phase thật,
  và cách cũ để máy mù giữa hai trạng thái chờ khác hẳn nhau.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-conventions` | project | NỀN | Nơi đặt khuôn chung và luật áp khuôn (đầu ra 1, 2) |
| `tdq-spec` | project | NỀN | Khối trình spec (đầu ra 6) |
| `tdq-plan` | project | NỀN | Khối trình plan và cổng mode (đầu ra 6, 8) |
| `tdq-intake` | project | NỀN | Câu hỏi pipeline, interview, cổng chế độ nhanh (đầu ra 7) |
| `tdq-build` | project | NỀN | Câu hỏi commit cuối request (đầu ra 7) |
| Đã xét 280 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — việc này chỉ sửa văn bản skill, hằng chuỗi và bảng phase, không tạo
  runtime mới. Đường log `_info`/`_warn` sẵn có trong `tdq_state.py` giữ nguyên.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `test_gate_merge.py` cấm chữ "turn mới" trong skill gate | Không thêm được luật chờ mode | Nới bất biến: chỉ cấm ở chặng spec → plan và mode → build, cho phép chặng plan → mode |
| `test_context_hooks.py` khẳng định cứng chuỗi `duyệt plan mode …` | Suite đỏ khi đổi `APPROVE_HINTS` | Sửa test cùng lượt, coi là một task riêng |
| `phases.md` là file TỰ SINH ở 2 nơi | Sửa tay sẽ lệch với hằng | Sinh lại bằng `tdq_state.py phases-doc`, có test khoá |
| `~/.claude/CLAUDE.md` §6 nằm NGOÀI repo, không track git | Luật cá nhân mâu thuẫn luồng mới | Sửa kèm và nêu rõ trong report; duyệt spec là duyệt cả việc này |
| Phase mới chen giữa `plan` và `implement` | Request đang dở của user khác kẹt | Phase `mode` chỉ vào khi `implement_mode` rỗng; có mode sẵn thì đi thẳng implement |
| `tdq-conventions/SKILL.md` trần 120 dòng | Không nhét thêm được luật | Đặt chi tiết khuôn ở file reference, `SKILL.md` chỉ giữ luật ngắn + link |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Khuôn chung tồn tại và sạch lint | `python3 scripts/doc_lint.py skills/tdq-conventions/references/user-facing-block.md` | exit 0 |
| Q2 | Quy ước áp khuôn cho đủ 7 chỗ | `grep -c "user-facing-block" skills/tdq-conventions/SKILL.md` | ≥ 1 và file ≤ 120 dòng |
| Q3 | Phase `mode` có thật và chỉ đúng việc | `python3 scripts/tdq_state.py phases-doc \| grep -c "^| mode "` | ra `1` |
| Q4 | `approve plan` không mode chạy được | `approve plan --by "duyệt plan"` trong project rác rồi `get implement_mode` | exit 0, mode rỗng, `plan_approved=true` |
| Q5 | Gợi ý duyệt plan bỏ mode, có gợi ý mode | `grep -n "APPROVE_HINTS" -A 12 hooks/scripts/_common.py` | khoá `plan` không chứa `mode`, có khoá `mode` |
| Q6 | Cổng mode giải thích 2 mode | `grep -c "subagent" skills/tdq-plan/SKILL.md` | ≥ 1 và đọc thấy 1 dòng nghĩa cho mỗi mode |
| Q7 | Tài liệu tự sinh khớp hằng | `python3 -m pytest tests/test_phase_table.py -q` | exit 0 |
| Q8 | Toàn bộ suite xanh | `python3 -m pytest tests/ -q` | exit 0 |

## 7. Câu hỏi còn mở

(rỗng)
