# SPEC — Dựng lại `portable/` cho Codex + cập nhật tài liệu project-level

Ngày: 2026-08-11 · Bản: 1.0 · Brief: ../brief/2026-08-11-cai-tdq-project-level.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: một project bất kỳ có thể bật tdq-workflow ở project-level cho cả Claude
  Code (đã có đường sẵn, chỉ thiếu tài liệu đúng) và Codex (đường đã mất từ khi
  `portable/` bị xoá ở 0.10.0 — cần dựng lại, khớp schema/quy tắc hiện hành).
- Trong phạm vi:
  - Dựng lại cây `portable/` trong repo TDQWorkflow (nguồn chung, không nhắm 1 project
    đích cụ thể) — nội dung dịch từ `skills/tdq-*/SKILL.md` hiện hành, KHÔNG phải khôi
    phục nguyên bản cũ đã lệch.
  - Sửa `docs/notes/user-level-install.md`: mục 4 (Codex) trỏ đúng `portable/` mới; mục
    1 làm rõ cách dùng ở scope project (không chỉ user); tiêu đề đầu file mở rộng phạm
    vi "user-level VÀ project-level".
  - Cập nhật `README.md` (mục Cài đặt) nếu cần trỏ tới `portable/` mới.
- NGOÀI phạm vi:
  - Không viết script tự động hoá cài đặt (đã chốt ở interview câu 3).
  - Không phục dựng mode `external`/deep-search (đã bỏ chủ đích từ 0.9.0/0.10.0).
  - Không test bằng Codex thật trên project mẫu (đã chốt ở interview câu 4 — QC bằng
    đối chiếu nội dung, không cần môi trường Codex).
  - Không đổi hành vi `scripts/tdq_state.py`, hooks, skills/ hiện tại — spec này chỉ
    thêm tài liệu mới + sửa tài liệu cũ.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích | CÓ | đã xong (brief đã chốt 4 câu hỏi) |
| Research web | BỎ | thuần nội bộ, đủ nguồn từ git history + skills/ hiện tại |
| Interview thêm | BỎ | hết câu hỏi làm đổi kết quả |
| QC độc lập (agent riêng) | BỎ | việc là tài liệu, tự đối chiếu nội dung với `scripts/tdq_state.py`/`skills/` là đủ |
| Implement | CÓ | tạo/sửa file thật (main mode — 1 turn, không cần chia sub-agent vì việc tuần tự, không song song hoá được) |
| Report | CÓ | bắt buộc theo full lane |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Hướng dẫn tổng + giao thức 1 turn cho Codex | `portable/AGENTS.md` | Có đủ 6 mục: pipeline, giao thức 1 turn, state CLI, duyệt, git, chất lượng — đối chiếu đúng `skills/tdq-conventions/SKILL.md` |
| 2 | Hướng dẫn copy sang project khác | `portable/README.md` | Liệt kê đúng 3 thứ cần copy (AGENTS.md, workflow/, scripts/tdq_state.py) + lệnh mẫu |
| 3 | Chi tiết phase intake (no_state, analyze, quick) | `portable/workflow/01-intake.md` | Khớp `skills/tdq-intake/SKILL.md` + `references/{analyze-full,interview,quick-lane}.md` (rút gọn, giữ đủ luật) |
| 4 | Chi tiết phase spec | `portable/workflow/02-spec.md` | Khớp `skills/tdq-spec/SKILL.md` |
| 5 | Chi tiết phase plan | `portable/workflow/03-plan.md` | Khớp `skills/tdq-plan/SKILL.md` |
| 6 | Chi tiết phase implement/QC/report | `portable/workflow/04-build.md` | Khớp `skills/tdq-build/SKILL.md` + `references/qc.md` (bỏ nhánh external) |
| 7 | Bảng phase tự sinh | `portable/workflow/phases.md` | Sinh bằng `python3 scripts/tdq_state.py phases-doc` (đúng lệnh output-path portable), diff = 0 với bản sinh cho `skills/tdq-conventions/references/phases.md` (cùng nguồn `PHASE_TABLE`) |
| 8 | Reference duyệt | `portable/workflow/references/approval.md` | Khớp `skills/tdq-conventions/references/approval.md` |
| 9 | Reference khuôn plan | `portable/workflow/references/plan-template.md` | Khớp `skills/tdq-plan/references/plan-template.md` |
| 10 | Reference QC | `portable/workflow/references/qc.md` | Khớp `skills/tdq-build/references/qc.md`, bỏ đoạn external |
| 11 | Reference lane quick | `portable/workflow/references/quick-lane.md` | Khớp `skills/tdq-intake/references/quick-lane.md` |
| 12 | `docs/notes/user-level-install.md` sửa mục 1/4 + tiêu đề | cùng file, không đổi tên | Mục 4 trỏ `portable/` mới, không còn câu lệnh/đường dẫn chết |
| 13 | `README.md` mục Cài đặt cập nhật (nếu cần) | `README.md` | Không còn nhắc `portable/` đã xoá như thể tồn tại; có dòng trỏ `docs/notes/user-level-install.md` cho Codex |

## 3. Cách tiếp cận & lý do
- Chọn: dịch trực tiếp từ `skills/tdq-*/SKILL.md` + references hiện hành sang dạng
  portable (không có hook, không có skill system → viết lại thành file .md đọc tuần tự,
  giữ nguyên luật nội dung, đổi cách gọi `${CLAUDE_PLUGIN_ROOT}/scripts/...` thành
  đường dẫn tương đối `scripts/tdq_state.py` từ root project đích).
- Vì: đây là cách duy nhất đảm bảo bản portable KHÔNG lệch behavior so với plugin
  Claude Code hiện tại (bản cũ đã lệch đúng vì copy 1 lần rồi không đồng bộ tiếp — xem
  `tests/test_portable_sync.py` cũ từng khoá việc này, đã xoá cùng `portable/`).
- Đã loại: khôi phục nguyên văn bản cũ qua `git show de76221^:portable/` — vì bản đó
  thiếu QC quick bắt buộc (0.9.0), thiếu brief gộp 3 mục, còn nhắc mode `external` đã
  bỏ — dùng lại sẽ tạo ra tài liệu sai ngay từ đầu.
- Đã loại: viết `portable/` như một skill Claude Code dùng chung — vì Codex không đọc
  được thư mục `skills/` của plugin (không có skill system), bắt buộc phải là file
  `AGENTS.md` độc lập theo đúng convention Codex.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Đã xét 90+ skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực (Unity, Adobe, Canva, Cloudflare, DB, browser automation…) — việc này thuần đọc/viết tài liệu nội bộ repo |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này chỉ sửa/tạo tài liệu (.md), không có runtime mã nguồn chạy được.
- Không placeholder, không TODO stub — mọi file portable phải có nội dung đầy đủ, không
  để trống chờ "điền sau".
- Mỗi thành phần có kiểm riêng: mỗi file portable đối chiếu bằng cách đọc song song với
  file nguồn tương ứng trong `skills/` (xem bảng QC §6) — không có "unit test" theo
  nghĩa code vì đây là tài liệu.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bản portable lệch behavior so với `skills/` ngay sau khi viết (không có test tự động khoá như `test_portable_sync.py` cũ) | Codex chạy sai luật, tự đoán bừa | Task cuối cùng của plan là đọc lại đối chiếu từng cặp file (portable ↔ skills nguồn) theo đúng bảng §2, liệt kê rõ trong QC — chấp nhận rủi ro không có test tự động (ngoài phạm vi, đã chốt ở lộ trình) |
| Sau này `skills/` đổi mà quên đồng bộ `portable/` | Portable lại lệch dần theo thời gian như bản cũ | Ghi rõ trong `portable/README.md`: "bản dịch thủ công, không tự sinh — sửa `skills/` xong nhớ đồng bộ tay `portable/`" để người sau biết rủi ro |
| `docs/notes/user-level-install.md` mục 1/3 sai lệch nếu sửa không cẩn thận (README/skills khác có thể trỏ tới) | Link chết, hướng dẫn sai | Chỉ sửa nội dung, giữ nguyên tên file (đã chốt interview câu 3) |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `portable/workflow/phases.md` đúng nguồn `PHASE_TABLE` | `python3 scripts/tdq_state.py phases-doc portable/workflow/phases.md` (hoặc lệnh tương đương output-path) rồi diff nội dung bảng phase với `skills/tdq-conventions/references/phases.md` | Bảng phase (tên, việc, lệnh chuyển tiếp) khớp 100%, chỉ khác đường dẫn gọi script |
| Q2 | Mỗi file portable/workflow/*.md không nhắc mode `external`/deep-search | `grep -rn "external\|deep.search" portable/` | Không có kết quả (trừ dòng lịch sử ghi chú nếu có, phải gắn nhãn rõ "đã bỏ") |
| Q3 | `portable/AGENTS.md` đối chiếu đủ 6 mục so với `skills/tdq-conventions/SKILL.md` | đọc song song 2 file, liệt kê từng mục có/thiếu | Đủ: pipeline, giao thức 1 turn, state CLI, duyệt (approval.md), git naming, chất lượng (log/placeholder/test) |
| Q4 | `docs/notes/user-level-install.md` không còn câu lệnh/đường dẫn chết | đọc lại toàn file, kiểm từng đường dẫn nêu trong đó thực sự tồn tại (`ls <path>`) | Mọi đường dẫn nêu trong file đều tồn tại trên đĩa |
| Q5 | `README.md` không còn mô tả `portable/` như đã xoá | đọc lại đoạn liên quan | Đoạn nhắc Codex trỏ đúng `docs/notes/user-level-install.md` hoặc `portable/README.md` |
| Q6 | Doc lint | `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-11-cai-tdq-project-level.md` | exit 0 |

DoD: cả 6 hạng mục Q1–Q6 PASS; `portable/` có đủ 10 file liệt kê ở §2 (#1–#11, `phases.md`
tính 1 trong đó); `docs/notes/user-level-install.md` và `README.md` đã cập nhật; working
log đã ghi.

## 7. Câu hỏi còn mở
(Rỗng.)
