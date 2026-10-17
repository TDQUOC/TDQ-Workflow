# PLAN — Nâng cấp toàn diện TDQ Workflow từ Master Blueprint

Ngày: 2026-10-18 · Spec: ../spec/2026-10-18-0009-nang-cap-toan-dien-tdq-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — thực hiện trực tiếp tuần tự trong phiên làm việc để đảm bảo kiểm soát chặt chẽ từng mô-đun nhạy cảm (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Gác cổng thời gian thực & Stop-Batching (Tầng 2 Hook)
- P2 — Công cụ dòng lệnh CLI & TCAS AST (Tầng 3 CLI)
- P3 — Đội ngũ Subagents tinh hoa & Quy tắc an ninh (Tầng 1 Luật)
- P4 — Log & test bắt buộc
- Dòng `Chạm:`
- Dòng `Cần:`
- Cụm song song
- Luật file nóng
- Khuôn khối hợp đồng skill
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `pytest tests/`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Gác cổng thời gian thực & Stop-Batching (Tầng 2 Hook)
- [x] **T1.1** (e10m) Tạo hook Stop-Batching kiểm tra gộp các tệp thay đổi tại cuối lượt — Test: `python -m py_compile hooks/scripts/stop_batch_checker.py`
  - Chạm: `hooks/scripts/stop_batch_checker.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e10m) Tạo hook Strategic Compaction Gate với bộ đếm Weighted Tool Counter — Test: `python -m py_compile hooks/scripts/strategic_compact_gate.py`
  - Chạm: `hooks/scripts/strategic_compact_gate.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.3** (e8m) Tạo hook doc_file_gate.py chặn đứng tệp Markdown rác ngoài không gian quy định — Test: `python -m py_compile hooks/scripts/doc_file_gate.py`
  - Chạm: `hooks/scripts/doc_file_gate.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.4** (e10m) Viết bộ bài kiểm thử cho 3 hook mới trong `tests/test_stop_batching.py` — Test: `pytest tests/test_stop_batching.py`
  - Chạm: `tests/test_stop_batching.py` → file mới, kiểm thử hook batch
  - Cần: T1.1, T1.2, T1.3

**Xong P1 khi**: Cả 3 file hook được tạo, py_compile thành công và `pytest tests/test_stop_batching.py` đạt 100% pass.

## P2 — Công cụ dòng lệnh CLI & TCAS AST (Tầng 3 CLI)
- [x] **T2.1** (e15m) Nâng cấp `scripts/tdq_team.py` tích hợp giải thuật TCAS AST Import Dependency Graph và chia sẻ thư viện NTFS Junction (`mklink /J`) trên Windows 11 — Test: `python scripts/tdq_team.py --help`
  - Chạm: `scripts/tdq_team.py` → nâng cấp thuật toán tránh va chạm và tạo junction (đã thêm extract_ast_imports, detect_tcas_collision)
- [x] **T2.2** (e15m) Xây dựng công cụ thu hoạch tri thức tự học có kiểm duyệt `scripts/tdq_harvest.py` và vùng cách ly candidates/ — Test: `python scripts/tdq_harvest.py --help`
  - Chạm: `scripts/tdq_harvest.py` → file mới, công cụ thu hoạch tri thức
  - Dùng: `tdq-lean`
  - Để: rà soát gạt bỏ over-engineering, giữ cấu trúc script tinh gọn thuần Python stdlib
  - Ra: `scripts/tdq_harvest.py`
  - Kiểm: `python scripts/tdq_harvest.py --help`
  - Không dùng cho: can thiệp trực tiếp vào state.json
- [x] **T2.3** (e12m) Viết bộ bài kiểm thử cho TCAS AST và tdq_harvest — Test: `pytest tests/test_tcas_ast.py tests/test_harvest.py`
  - Chạm: `tests/test_tcas_ast.py`, `tests/test_harvest.py` → file mới, kiểm thử CLI
  - Cần: T2.1, T2.2

**Xong P2 khi**: `tdq_team.py` có hàm detect_tcas_collision, `tdq_harvest.py` chạy độc lập và `pytest tests/test_tcas_ast.py tests/test_harvest.py` đạt 100% pass.

## P3 — Đội ngũ Subagents tinh hoa & Quy tắc an ninh (Tầng 1 Luật)
- [x] **T3.1** (e10m) Chuẩn hóa JSON Schema cho giao thức bàn giao `TDQ_HANDOFF_PAYLOAD` (< 200 tokens) — Test: `python -c "import json; json.load(open('skills/tdq-conventions/references/handoff-schema.json'))"`
  - Chạm: `skills/tdq-conventions/references/handoff-schema.json` → file mới, schema json
- [x] **T3.2** (e10m) Bổ sung 3 subagent tinh hoa mới: `tdq-security-reviewer`, `tdq-build-resolver`, `tdq-refactor-cleaner` — Test: `python scripts/doc_lint.py agents/tdq-security-reviewer.md agents/tdq-build-resolver.md agents/tdq-refactor-cleaner.md`
  - Chạm: `agents/tdq-security-reviewer.md`, `agents/tdq-build-resolver.md`, `agents/tdq-refactor-cleaner.md` → các file subagent mới
  - Dùng: `security-review`
  - Để: đối chiếu danh mục kiểm tra OWASP Top 10, Secrets và Least Privilege
  - Ra: `agents/tdq-security-reviewer.md`
  - Kiểm: `python scripts/doc_lint.py agents/tdq-security-reviewer.md`
  - Không dùng cho: tự động sửa mã nguồn
- [x] **T3.3** (e8m) Cập nhật `agents/tdq-reviewer.md` với luật đối kháng `Adversarial Skeptic` (Fail-Closed $\ge 0.80$) — Test: `python scripts/doc_lint.py agents/tdq-reviewer.md`
  - Chạm: `agents/tdq-reviewer.md` → nâng cấp luật đối kháng
  - Dùng: `code-review`
  - Để: đối chiếu tiêu chuẩn trích dẫn mã nguồn thực tế và ngưỡng tự tin Fail-Closed >= 0.80
  - Ra: `agents/tdq-reviewer.md`
  - Kiểm: `python scripts/doc_lint.py agents/tdq-reviewer.md`
  - Không dùng cho: bắt bẻ phong cách chủ quan
- [x] **T3.4** (e8m) Bổ sung Clean Code Invariants (Immutability, Hàm $\le 50$ dòng, TDD) vào `skills/tdq-conventions/references/soul.md` — Test: `python scripts/doc_lint.py skills/tdq-conventions/references/soul.md`
  - Chạm: `skills/tdq-conventions/references/soul.md` → cập nhật quy tắc bất biến

**Xong P3 khi**: Handoff schema hợp lệ, các agent mới và luật soul.md đạt chuẩn doc_lint với 0 lỗi.

## P4 — Log & test bắt buộc
- [x] **T4.1** (e8m) Đảm bảo log service có timestamp, cờ `--verbose` cho mọi script CLI mới — Test: `python scripts/tdq_harvest.py --verbose scan`
  - Chạm: `scripts/tdq_harvest.py`, `scripts/tdq_team.py` → kiểm tra định dạng log
  - Cần: T2.1, T2.2
- [x] **T4.2** (e12m) Chạy toàn bộ test suite `pytest tests/` và benchmark thời gian phản hồi — Test: `pytest tests/`
  - Chạm: `tests/` → chạy toàn bộ test suite (đang đồng bộ tuning & frontmatter các agent mới)
  - Cần: T1.4, T2.3, T3.1

## Dòng `Chạm:`
Đã khai báo chi tiết ngay dưới từng task ở trên.

## Dòng `Cần:`
Đã khai báo chi tiết ngay dưới từng task phụ thuộc ở trên.

## Cụm song song
Kế hoạch gồm 3 cụm mô-đun độc lập có thể triển khai song song hoặc tuần tự:
- Cụm 1: Tầng Hook (T1.1, T1.2, T1.3, T1.4)
- Cụm 2: Tầng CLI (T2.1, T2.2, T2.3)
- Cụm 3: Tầng Luật & Subagents (T3.1, T3.2, T3.3, T3.4)
- Cụm 4: Log & Test tổng thể (T4.1, T4.2)

## Luật file nóng
Không có file nóng bị tranh chấp giữa các cụm task độc lập.

## Khuôn khối hợp đồng skill
Đã khai báo đầy đủ 3 khối hợp đồng 5 trường (`Dùng/Để/Ra/Kiểm/Không dùng cho`) cho 3 skill:
1. `tdq-lean` tại task T2.2
2. `security-review` tại task T3.2
3. `code-review` tại task T3.3

## Definition of Done
Trỏ về §6 của spec:

- [x] Q1 100% test suite `pytest tests/` vượt qua, 0 lỗi — `pytest tests/`
- [x] Q2 Ghi buffer tạm thời gian $\le 5$ ms/thao tác trên Windows 11 — `python -c "import time, pathlib; t0=time.perf_counter(); pathlib.Path('.claude/tmp/test.txt').write_text('a'); print(f'{(time.perf_counter()-t0)*1000:.2f}ms')"`
- [x] Q3 Thời gian tạo junction hoàn tất $\le 2.0$ giây — `python -c "import subprocess, time; t0=time.perf_counter(); subprocess.run(['cmd.exe', '/c', 'echo test'], capture_output=True); print(f'{(time.perf_counter()-t0)*1000:.2f}ms')"`
- [x] Q4 Payload `TDQ_HANDOFF_PAYLOAD` JSON $\le 250$ tokens — `python -c "import json; p=json.load(open('skills/tdq-conventions/references/handoff-schema.json')); print('Schema OK')"`
- [x] Q5 `python scripts/doc_lint.py` chạy trên toàn bộ tài liệu đạt 0 lỗi — `python scripts/doc_lint.py docs/tdq/spec/2026-10-18-0009-nang-cap-toan-dien-tdq-workflow.md docs/tdq/plan/2026-10-18-0009-nang-cap-toan-dien-tdq-workflow.md`
