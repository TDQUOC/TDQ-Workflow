# PLAN — Trình bày thân thiện ở mọi chỗ giao tiếp với user

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-trinh-bay-than-thien-duyet.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — mọi task đụng chung `tdq_state.py`, `_common.py` và các file skill liên quan chặt, tách worktree sẽ xung đột. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Khuôn trình bày dùng chung

- [x] **T1.1** (n3 e10m) Viết `skills/tdq-conventions/references/user-facing-block.md`: 5 thành phần khuôn (đường kẻ ngăn, tiêu đề in đậm, câu dẫn xưng "bạn", đường dẫn file đầy đủ, dòng `➤` cuối), cấm emoji, kèm 1 ví dụ mẫu — Test: `python3 scripts/doc_lint.py skills/tdq-conventions/references/user-facing-block.md` exit 0
- [x] **T1.2** (n3 e8m) Thêm luật vào `skills/tdq-conventions/SKILL.md` §1: mọi khối hỏi user theo khuôn ở T1.1, liệt kê đủ 7 chỗ giao tiếp — Test: `grep -c "user-facing-block" skills/tdq-conventions/SKILL.md` ≥ 1 và `wc -l` ≤ 120
- [x] **T1.3** (n3 e8m) `tests/test_user_facing_block.py`: file khuôn tồn tại, nêu đủ 5 thành phần, không chứa emoji; `SKILL.md` trỏ tới nó — Test: `python3 -m pytest tests/test_user_facing_block.py -q` xanh

**Xong P1 khi**: file khuôn có thật, `SKILL.md` trỏ tới nó và ≤ 120 dòng, test mới xanh.

## P2 — Phase `mode` trong máy

- [x] **T2.1** (n8 e20m) Thêm `mode` vào `VALID_PHASES`, `PHASE_ORDER`, `PHASE_TABLE` (entry: `plan_approved` true mà `implement_mode` rỗng · action: giải thích 2 mode rồi hỏi · cmd: `approve plan --mode <main|subagent> --by "<nguyên văn>"` · forbidden: sửa code, tự chọn mode thay user); phase `plan` đổi cmd thành `approve plan --by "<nguyên văn>"` và checklist trỏ sang phase `mode` — Test: `python3 -m pytest tests/test_phase_table.py -q` xanh sau khi sinh lại doc
- [x] **T2.2** (n5 e12m) `approve plan` không kèm `--mode` tự đẩy `phase=mode`; kèm `--mode` thì đẩy thẳng `phase=implement` — Test: `TDQ_PROJECT_DIR=<tmp>` chạy 2 kịch bản, `get phase` ra `mode` và `implement`
- [x] **T2.3** (n5 e12m) `_common.py`: khoá `plan` trong `APPROVE_HINTS` bỏ phần mode, thêm khoá `mode` có giải thích ngắn 2 mode; `approve_hint` xử lý khoá mới — Test: `python3 -m pytest tests/test_context_hooks.py -q` xanh sau khi cập nhật kỳ vọng
- [x] **T2.4** (n5 e12m) `prompt_context.py`: thêm trạng thái chờ `mode` (plan đã duyệt mà `implement_mode` rỗng) và nhận diện câu trả lời chọn mode — Test: giả lập payload prompt `"main"` ở trạng thái chờ mode, hook in dòng `[TDQ:APPROVE]` có `--mode main`
- [x] **T2.5** (n5 e15m) `tests/test_mode_phase.py`: bao 4 nhánh — duyệt plan không mode → phase `mode`; duyệt plan kèm mode → phase `implement`; `PHASE_TABLE["mode"]` đủ 6 trường; `phase_key` trả `mode` đúng lúc — Test: `python3 -m pytest tests/test_mode_phase.py -q` xanh

**Xong P2 khi**: `tdq_state.py next` ở trạng thái plan-đã-duyệt-chưa-có-mode in ra phase `mode`, mọi test P2 xanh.

## P3 — Áp khuôn vào các chỗ giao tiếp

- [x] **T3.1** (n5 e12m) `skills/tdq-spec/SKILL.md` bước 4: viết lại khối trình spec theo khuôn T1.1 (câu dẫn "bạn", đường dẫn spec đầy đủ, khối duyệt tách riêng) — Test: `grep -n "user-facing-block" skills/tdq-spec/SKILL.md` có kết quả và `doc_lint` exit 0
- [x] **T3.2** (n8 e20m) `skills/tdq-plan/SKILL.md`: bước 5 trình plan theo khuôn, dòng duyệt chỉ còn `duyệt plan`; thêm bước 6 mới — cổng `mode` với 1 dòng giải thích cho `main` và 1 dòng cho `subagent`; giữ luật user nói mode sẵn thì bỏ qua cổng; sửa cả dòng `description` của skill cho khớp luồng 2 bước và giữ file ≤ 100 dòng — Test: `grep -c "duyệt plan mode" skills/tdq-plan/SKILL.md` ra `0`; `python3 scripts/doc_lint.py skills/tdq-plan/SKILL.md` exit 0 (gồm trần 100 dòng)
  - Ghi chú T3.2: khối `mode` mới làm file vượt trần 100 dòng → nén các đoạn dài ở bước
    1, 2, 3, 5 (không bỏ luật nào) để về đúng trần. Chi tiết cách chấm `(nN)`/`eNm` đã có
    sẵn trong `plan-template.md` nên ở SKILL.md chỉ giữ 3 dòng luật, không chép lại.
- [x] **T3.3** (n3 e10m) Áp khuôn cho câu hỏi chọn pipeline và vòng interview: `skills/tdq-intake/references/lane-decision.md`, `interview.md` — Test: `doc_lint` exit 0 trên 2 file, mỗi file trỏ tới `user-facing-block`
- [x] **T3.4** (n3 e10m) Áp khuôn cho cổng chế độ nhanh (`skills/tdq-intake/references/quick-lane.md`) và câu hỏi commit cuối request (`skills/tdq-build/SKILL.md` bước 10) — Test: `doc_lint` exit 0 trên 2 file, mỗi file trỏ tới `user-facing-block`
- [x] **T3.5** (n5 e12m) Nới `tests/test_gate_merge.py`: vẫn cấm bắt user chờ thêm turn ở chặng spec → plan và mode → build; cho phép ở chặng plan → mode, kèm test khẳng định cổng mode có mặt trong `tdq-plan` — Test: `python3 -m pytest tests/test_gate_merge.py -q` xanh

**Xong P3 khi**: cả 7 chỗ giao tiếp dùng khuôn chung, không còn chuỗi `duyệt plan mode` trong skill.

## P4 — Đồng bộ tài liệu kéo theo

- [x] **T4.1** (n3 e8m) Sinh lại `skills/tdq-conventions/references/phases.md` và `portable/workflow/phases.md` bằng `tdq_state.py phases-doc` — Test: `python3 -m pytest tests/test_phase_table.py::PhaseTableTest::test_docs_match_constant -q` xanh
- [x] **T4.2** (n3 e6m) `portable/workflow/*`: sửa `03-plan.md` sang luồng 2 bước, thêm bản portable của `references/user-facing-block.md`, sửa `references/plan-template.md` — Test: `grep -rn "duyệt plan mode" portable/` không còn kết quả
- [x] **T4.4** (n2 e4m) `docs/claude-md-mau.md` §6 sang luồng 2 bước, sửa nốt `skills/tdq-plan/references/plan-template.md` — Test: `grep -rn "duyệt plan kèm mode" docs/claude-md-mau.md portable/` không còn kết quả (working log, spec/brief/report cũ là sổ ghi lịch sử, cố ý giữ nguyên)
- [x] **T4.3** (n1 e5m) Sửa `~/.claude/CLAUDE.md` §6 sang luồng 2 bước (file ngoài repo, user đã duyệt kèm spec) — Test: `grep -n "duyệt plan" ~/.claude/CLAUDE.md` cho thấy câu mới, không còn "kèm mode"

**Xong P4 khi**: không còn tài liệu nào mô tả luồng gộp mode cũ.

## P5 — Log & test bắt buộc

Log: BỎ — việc này chỉ sửa văn bản skill, hằng chuỗi và bảng phase, không tạo runtime mới;
đường log `_info`/`_warn` sẵn có trong `tdq_state.py` giữ nguyên.

- [x] **T5.1** (n3 e10m) Chạy full suite một lần, sửa mọi test đỏ do đổi chuỗi/luồng — Test: `python3 -m pytest tests/ -q` exit 0

**Xong P5 khi**: toàn bộ suite xanh.

## Definition of Done

Trỏ về §6 của spec — 8 hạng mục:

1. Q1 `python3 scripts/doc_lint.py skills/tdq-conventions/references/user-facing-block.md` → exit 0.
2. Q2 `grep -c "user-facing-block" skills/tdq-conventions/SKILL.md` ≥ 1 và `wc -l` ≤ 120.
3. Q3 `python3 scripts/tdq_state.py phases-doc | grep -c "^| \`mode\`"` → `1`.
4. Q4 `approve plan --by "duyệt plan"` trong project tạm → exit 0, `implement_mode` rỗng, `plan_approved` true.
5. Q5 `grep -n "APPROVE_HINTS" -A 12 hooks/scripts/_common.py` → khoá `plan` không chứa `mode`, có khoá `mode`.
6. Q6 `grep -c "subagent" skills/tdq-plan/SKILL.md` ≥ 1 và có 1 dòng nghĩa cho mỗi mode.
7. Q7 `python3 -m pytest tests/test_phase_table.py -q` → exit 0.
8. Q8 `python3 -m pytest tests/ -q` → exit 0.
