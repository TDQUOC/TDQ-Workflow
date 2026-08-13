# PLAN — Dựng lại `portable/` cho Codex + cập nhật tài liệu project-level

Ngày: 2026-08-11 · Spec: ../spec/2026-08-11-cai-tdq-project-level.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 11 file phụ thuộc chặt lẫn nhau (AGENTS.md trỏ workflow/*, phases.md
sinh từ cùng `PHASE_TABLE`, các reference dùng chung thuật ngữ) + việc thuần đọc/dịch tài
liệu tuần tự, không có phần nào tách song song có lợi (ĐỀ XUẤT, user chốt lúc duyệt).
Trạng thái plan: HOÀN THÀNH (mode main, "duyệt plan mode main" 2026-08-11 20:31)

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Khung `portable/` + core AGENTS.md/README.md
- [x] **T1.1** (n2) Tạo `portable/AGENTS.md`: dịch từ `skills/tdq-conventions/SKILL.md`
  đủ 6 mục (pipeline, giao thức 1 turn, state CLI, duyệt, git naming, chất lượng) +
  bảng trỏ file phase (`workflow/01-04-*.md`) — Test: đọc song song 2 file, checklist
  6 mục đều có mặt, không nhắc `external`/deep-search.
- [x] **T1.2** (n2) Tạo `portable/README.md`: hướng dẫn copy 3 thứ (`AGENTS.md`,
  `workflow/`, `scripts/tdq_state.py`) sang project đích + lệnh mẫu + cảnh báo "bản dịch
  thủ công, không tự sinh — sửa `skills/` xong nhớ đồng bộ tay" — Test: đọc lại đủ 3 mục
  (nội dung copy, lệnh mẫu, cảnh báo đồng bộ).

**Xong P1 khi**: 2 file tồn tại, không rỗng, không nhắc mode `external`.

## P2 — Dịch 4 file phase workflow
- [x] **T2.1** (n3) Tạo `portable/workflow/01-intake.md`: dịch từ
  `skills/tdq-intake/SKILL.md` + `references/{analyze-full,interview,quick-lane}.md`
  (gộp rút gọn, giữ đủ luật: tầng nhỏ, Phần A/B/C, khuôn interview, quick-lane 9 bước)
  — Test: đối chiếu từng luật con trong `skills/tdq-intake/SKILL.md`, không thiếu mục nào.
- [x] **T2.2** (n2) Tạo `portable/workflow/02-spec.md`: dịch từ `skills/tdq-spec/SKILL.md`
  (5 bước; khuôn spec gộp thẳng vào file này thay vì tách `spec-template.md` riêng, để
  giữ đúng 11 file như spec §2) — Test: đối chiếu 5 bước đều có mặt.
- [x] **T2.3** (n2) Tạo `portable/workflow/03-plan.md`: dịch từ `skills/tdq-plan/SKILL.md`
  (6 bước, luật mode đề xuất, điểm `(nN)`, nhãn `(mcp)`) — Test: đối chiếu 6 bước.
- [x] **T2.4** (n3) Tạo `portable/workflow/04-build.md`: dịch từ `skills/tdq-build/SKILL.md`
  (implement/QC/report full lane, KHÔNG có nhánh external/split-plan; report-template gộp
  thẳng vào file này thay vì tách riêng, để giữ đúng 11 file) — Test: đối chiếu nội dung,
  `grep -n "external"` không ra kết quả.

**Xong P2 khi**: 4 file tồn tại, mỗi file đối chiếu đủ số bước như skill nguồn.

## P3 — 4 file reference + phases.md tự sinh
- [x] **T3.1** (n2) Tạo `portable/workflow/references/approval.md`: dịch từ
  `skills/tdq-conventions/references/approval.md` — Test: đối chiếu nội dung 2 file.
- [x] **T3.2** (n2) Tạo `portable/workflow/references/plan-template.md`: dịch từ
  `skills/tdq-plan/references/plan-template.md` (giữ nguyên khuôn `(nN)`, khối hợp đồng
  skill, nhãn `(mcp)`) — Test: đối chiếu 2 file, khuôn task mẫu giống hệt cấu trúc.
- [x] **T3.3** (n3) Tạo `portable/workflow/references/qc.md`: dịch từ
  `skills/tdq-build/references/qc.md`, bỏ mọi đoạn nhắc `external`/`split-plan` — Test:
  `grep -n "external\|split-plan" portable/workflow/references/qc.md` không ra kết quả.
- [x] **T3.4** (n2) Tạo `portable/workflow/references/quick-lane.md`: dịch từ
  `skills/tdq-intake/references/quick-lane.md` (9 bước, QC quick mặc định BẬT,
  `--no-qc` opt-out) — Test: đối chiếu đủ 9 bước + luật `--no-qc`.
- [x] **T3.5** (n2) Sinh `portable/workflow/phases.md` bằng
  `python3 scripts/tdq_state.py phases-doc portable/workflow/phases.md` (dùng path
  output khác `skills/tdq-conventions/references/phases.md`) — Test: file sinh ra
  không rỗng; `diff <(sed 's#skills/tdq-conventions/references/phases.md##' ...)` hoặc
  đối chiếu thủ công bảng phase giữa 2 file khớp 100% nội dung cột (chỉ khác dòng ghi
  chú đường dẫn nếu có).

**Xong P3 khi**: 5 file tồn tại, `phases.md` sinh thành công không lỗi.

## P4 — Cập nhật tài liệu cài đặt
- [x] **T4.1** (n3) Sửa `docs/notes/user-level-install.md`: đổi tiêu đề đầu file thành
  phạm vi "user-level VÀ project-level"; mục 1 làm rõ scope project (bỏ `--scope user`
  cho trường hợp chỉ dùng 1 project); mục 4 thay nội dung cũ ("copy portable/AGENTS.md…")
  bằng hướng dẫn đúng trỏ `portable/README.md` mới trong repo này — Test: `grep -n
  "portable/" docs/notes/user-level-install.md` chỉ ra đường dẫn còn tồn tại
  (`ls portable/README.md` phải thành công).
- [x] **T4.2** (n2) Kiểm `README.md` mục Cài đặt: nếu có câu nhắc `portable/` như đã
  xoá hoặc không tồn tại thì sửa lại trỏ đúng `docs/notes/user-level-install.md` mục 4
  — Test: đọc lại đoạn liên quan, không còn câu sai lệch thực tế. (Kiểm: `grep -n
  "portable" README.md` không ra kết quả nào ngoài dòng quy ước tên nhánh — README chưa
  từng mô tả `portable/` là đã xoá, không cần sửa.)

**Xong P4 khi**: cả 2 file không còn đường dẫn/câu lệnh chết liên quan `portable/`.

## Px — Log & test bắt buộc
Log: BỎ — việc này chỉ tạo/sửa file tài liệu (.md), không có runtime mã nguồn chạy được.

- [x] **Tx.1** (n2) Unit test: không cần thêm file test mới (đây là tài liệu) — thay
  bằng task đối chiếu tổng: đọc lại toàn bộ `portable/` so với bảng §2 spec, xác nhận đủ
  11 file — Test: `find portable -type f | wc -l` = 11 (`AGENTS.md`, `README.md`, 4 file
  `workflow/0*.md`, `workflow/phases.md`, 4 file `workflow/references/*.md`). PASS —
  `find portable -type f | wc -l` → 11, đúng danh sách.

**Xong Px khi**: đếm đủ 11 file, không thiếu không thừa.

## P5 — QC & Definition of Done
- [x] **T5.1** (n2) Chạy Q1: đối chiếu `portable/workflow/phases.md` với
  `skills/tdq-conventions/references/phases.md` — Test: bảng phase (tên, việc, lệnh
  chuyển tiếp) khớp nội dung. PASS.
- [x] **T5.2** (n1) Chạy Q2: `grep -rn "external\|deep.search" portable/` — Test:
  không có kết quả (hoặc chỉ có ghi chú lịch sử gắn nhãn rõ "đã bỏ"). PASS.
- [x] **T5.3** (n2) Chạy Q3: đối chiếu `portable/AGENTS.md` với
  `skills/tdq-conventions/SKILL.md` — Test: đủ 6 mục như spec liệt kê. PASS.
- [x] **T5.4** (n2) Chạy Q4: đọc lại `docs/notes/user-level-install.md`, kiểm từng
  đường dẫn nêu trong đó tồn tại trên đĩa (`ls <path>` cho mỗi đường dẫn) — Test: mọi
  lệnh `ls` đều thành công (exit 0). PASS.
- [x] **T5.5** (n1) Chạy Q5: đọc lại đoạn Codex trong `README.md` — Test: không còn
  mô tả `portable/` như đã xoá. PASS.
- [x] **T5.6** (n1) Chạy Q6: `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-11-cai-tdq-project-level.md`
  — Test: exit 0. PASS.

**Xong P5 khi**: Q1–Q6 đều PASS, ghi bằng chứng vào mục `## QC` phía dưới.

## QC

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | `phases.md` khớp `PHASE_TABLE` | `diff portable/workflow/phases.md skills/tdq-conventions/references/phases.md` | chỉ khác tiền tố đường dẫn `${CLAUDE_PLUGIN_ROOT}/scripts/` vs `scripts/` (đúng như thiết kế 2 bản), mọi cột nội dung khớp | PASS |
| Q2 | Không còn nhắc `external`/deep-search | `grep -rn "external\|deep.search" portable/` | 1 kết quả duy nhất: `portable/README.md:23` — ghi chú lịch sử "đã xoá cùng lần dọn mode `external` ở 0.10.0", gắn nhãn rõ đã bỏ | PASS |
| Q3 | `AGENTS.md` đủ mục so với `skills/tdq-conventions/SKILL.md` | `grep -n "^## " portable/AGENTS.md` | 10 heading: Pipeline + 8 mục số (1 Giao thức, 2 State, 3 Duyệt, 4 Cây tài liệu, 5 Working log, 6 Git, 7 Research, 8 Chất lượng) + "Không có ở bản portable này" — bao trọn 6 mục spec liệt kê | PASS |
| Q4 | Đường dẫn trong `user-level-install.md` không chết | `ls` từng path: `portable/README.md`, `portable/AGENTS.md`, `portable/workflow`, `scripts/tdq_state.py`, `docs/notes/user-level-install.md` | cả 5 lệnh `ls` exit 0 | PASS |
| Q5 | `README.md` không mô tả `portable/` là đã xoá | `grep -n "portable" README.md` | không có kết quả nào (README chưa từng nhắc `portable/`, không có câu sai lệch) | PASS |
| Q6 | `doc_lint.py` trên spec | `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-11-cai-tdq-project-level.md` | exit 0 | PASS |
| Q7 (cộng thêm, DoD) | Đủ 11 file `portable/` | `find portable -type f \| wc -l` | 11 | PASS |

Kết luận: PASS toàn bộ, không có FAIL, không cần vòng fix.

## Definition of Done
Trỏ về §6 spec `2026-08-11-cai-tdq-project-level.md`:
- Q1: `portable/workflow/phases.md` khớp `PHASE_TABLE` (đối chiếu nội dung với bản sinh trong `skills/`).
- Q2: không còn nhắc mode `external`/deep-search trong `portable/`.
- Q3: `portable/AGENTS.md` đủ 6 mục so với `skills/tdq-conventions/SKILL.md`.
- Q4: `docs/notes/user-level-install.md` không còn đường dẫn/lệnh chết.
- Q5: `README.md` không còn mô tả sai về `portable/`.
- Q6: `doc_lint.py` trên spec exit 0.
- Đủ 11 file trong `portable/` đúng bảng §2 spec.
