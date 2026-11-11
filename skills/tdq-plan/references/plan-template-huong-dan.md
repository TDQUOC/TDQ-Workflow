# Guidance for whoever WRITES the plan

Split out of `plan-template.md` on 2026-10-02. The three sections below are about writing and
self-checking, not about what gets copied into the plan — so they do not belong in context every
time a plan is written. The line-index block at the top of this file gives each section's exact
line range.

## The minute estimate `(eNm)` — six rules, and what it does NOT promise

`eNm` = the number of **minutes** Claude estimates it needs to EXECUTE that task itself (agent
runtime, not human waiting time). The unit is always minutes, an integer 1–999, never `1h` or
`0.5m`. The ETA of the whole plan = the sum of `eNm` over unfinished tasks.

- Score it as you write the task, never score it later.
- Estimate the time spent WORKING, not the time waiting for approval or interview answers.
- Unsure → score the number you actually believe, do not pad for safety.
- `eNm` is **optional**: missing on a task means that task is skipped in the ETA sum, and the
  plan still runs.
- `eNm` changes nothing about the tick rule `[ ] [~] [x]`: a `(e60m)` task ticks like a `(e5m)` one.
- `eNm` is NOT a promise of time to the user — it is the number the report compares to reality.

## The `Mode thực thi` line <!-- i18n-allow: canonical line name of the plan -->

- It MUST sit on **a line of its own**, never merged into another header line — tooling reads it.
- The value here is the **machine identifier**: `main`, `subagent` or `codex`. Which of them the
  machine can actually offer is what `tdq_state.py modes --json` answers; the labels the user
  reads at gate `mode` live in [mode-gate.md](mode-gate.md).
- This is only Claude's **proposal**. After the user approves the plan, phase `mode` asks; the
  mode written into state is the one the user SAID, never the proposal taken as settled. An
  approval sentence that already names a mode skips that gate and goes straight to implement.

## Check before presenting

- Every output in spec §2 maps to ≥ 1 task.
- Every task holds exactly one piece of work and one measurable check — no task shaped like
  "finish X".
- The first task of each phase opens a red → green path early.
- No task depends on a task placed after it.

## Phân tầng thích ứng (Adaptive Granularity)

- **Task can thiệp mã nguồn** (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.c`, `.cpp`, `.cs`...):
  BẮT BUỘC dùng cấu trúc **Self-Contained Task Block** đầy đủ (8 trường con: `Chạm:`, `Cần:`, `Mục tiêu:`, `Vị trí neo:`, `Công cụ:`, `Ràng buộc:`, `Đặc tả kỹ thuật:`, `Logic cốt lõi:`, `Ca góc hiểm & TDD:`). Linter Rule R15 tự động cưỡng chế chặn cứng (exit 1) nếu phát hiện task sửa code mà thiếu khối đặc tả kỹ thuật / pseudo-code.
- **Task tài liệu, cấu hình, template** (`.md`, `.json`, `.yaml`, `.txt`...):
  Cho phép dùng dạng **Compact** ngắn gọn: dòng task 1 dòng `- [ ] **Tx.y** (eNm) <nội dung> — Test: <lệnh>` kèm `Chạm:` nếu chạm nhiều file. Không ép buộc khối đặc tả hàm hay pseudo-code để tối ưu token.

## 4 chốt an toàn cơ học cho Model nhỏ (30B / Haiku)

Mọi task can thiệp mã nguồn BẮT BUỘC tích hợp 4 chốt an toàn cơ học trong Task Block:
1. **Vị trí neo chính xác (Exact Insertion Anchor):** Nêu rõ hàm đứng trước và đứng sau thay vì chỉ dùng số dòng. Cách này giúp model giữ định vị không gian trong file lớn trên 1.000 dòng.
2. **Chỉ thị công cụ dứt khoát (Tool Directives):** Bắt buộc dùng `Edit` trên file có sẵn, CẤM dùng `Write` để triệt tiêu lỗi cắt cụt mã (`# ... rest of code unchanged ...`). Chỉ dùng `Write` khi tạo file mới 100%.
3. **Đoạn mã Assertion cụ thể (Concrete Test Snippets):** Cung cấp cú pháp assert cụ thể trong phần `Ca góc hiểm & TDD` để chống bẫy assert mù (`ANTI-2 Blind Assertion`).
4. **Bất biến môi trường (Environment Invariants):** Giới hạn thư viện thuần stdlib, cấm tự ý cài đặt hoặc import thư viện lạ để tránh ảo giác dependency.
