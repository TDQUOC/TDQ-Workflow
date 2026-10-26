# PLAN — Giảm timeout và thời gian chờ agent-lsp

Ngày: 2026-10-26 · Spec: ../spec/2026-10-26-0224-giam-timeout-agent-lsp.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐỀ XUẤT: 8 tasks liên kết chặt qua cấu hình hook, luật tìm kiếm và sổ quan sát chung; thực thi tuần tự trong main process để kiểm soát trạng thái hook và tránh xung đột băm token-budget (user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau
- P1 — Chính sách chọn công cụ và giới hạn chờ 90 giây (O1, O2)
- P2 — Cổng kiểm soát blast_radius và ngắt mạch theo workspace (O3)
- P3 — Sổ quan sát thời gian chạy và phân loại kết quả LSP (O4)
- P4 — Thống kê p50/p95 và đối chiếu độ phủ caller oracle (O5)
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Luật file nóng (một file, nhiều task chạm)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)
- Px — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy test trước để xác nhận đỏ (hoặc viết test đỏ) → sửa code/tài liệu → chạy lại test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `python scripts/tdq_test.py vung-cham`; trọn bộ `python scripts/tdq_test.py tron-bo` chỉ chạy ở QC.
4. Lệnh nào chạm state của workflow trong test phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Luồng thực thi | Agent bị chỉ thị upstream thúc gọi `blast_radius` trước mọi thao tác sửa; client chờ mặc định 1.800 giây khi server treo; `lsp_gate.py` chỉ kiểm `start_lsp`; `search_observe.py` chỉ ghi nhận mốc gọi khái niệm, không ghi kết quả hay thời gian chạy | Hướng dẫn TDQ ghi đè rõ chỉ thị `blast_radius` tràn lan; `tdq_setup.py` cấu hình trần chờ 90 giây; `lsp_gate.py` chặn `blast_radius` vượt ngưỡng hoặc khi workspace đang mở mạch ngắt; `search_observe.py` và `search_replay.py` đo trọn vẹn `duration_ms`, `outcome` và độ phủ caller |
| Thành phần chạm | `uu-tien-tim-kiem.md` còn mâu thuẫn giữa dòng 21 và dòng 72; `hooks.json` thiếu `PostToolUseFailure` và chưa nối `blast_radius` vào `lsp_gate.py`; `search_replay.py` bỏ qua `tool_result` | Đồng bộ 2 tệp tài liệu, `tdq_setup.py`, `hooks.json`, `lsp_gate.py`, `search_observe.py`, `search_rules.py`, `search_replay.py` và 6 bộ kiểm thử |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu trực tiếp bản xem trước Archify explainer đã duyệt tại `docs/tdq/artifacts/2026-10-26-0224-giam-timeout-agent-lsp/preview.html` và manifest `docs/tdq/artifacts/2026-10-26-0224-giam-timeout-agent-lsp/preview.manifest.json`. WBS dưới đây ánh xạ 1-1 tới 4 nút trong sơ đồ `lsp-timeout-flow` (`setup` → `gate` → `observe` → `replay`). Kiểm tra binding bằng `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-10-26-0224-giam-timeout-agent-lsp.md --manifest docs/tdq/artifacts/2026-10-26-0224-giam-timeout-agent-lsp/preview.manifest.json` trước khi viết code.

## P1 — Chính sách chọn công cụ và giới hạn chờ 90 giây (O1, O2)

- [x] **T1.1** (e10m) Cập nhật `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `uu-tien-tim-kiem-chi-tiet.md` và `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` để trung hòa chỉ thị gọi `blast_radius` của server MCP, sửa mâu thuẫn phân loại giữa dòng 21 và bảng dòng 72; cập nhật `docs/claude-md-mau.md` và chạy cập nhật chỉ mục, ngân sách token — Test: `python -m pytest tests/test_claude_md_core.py tests/test_doc_index.py tests/test_token_budget.py -q`
  - Chạm: `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md`, `scripts/tdq_setup.py`, `docs/claude-md-mau.md`, `docs/tdq/token-budget.json`, `docs/tdq/audit/luat-hien-co.md`
  - Dùng: `update-config`
  - Để: Rà soát cấu trúc instruction ghim và phân vùng cấu hình người dùng trước khi cập nhật
  - Ra: `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `scripts/tdq_setup.py`, `docs/claude-md-mau.md`
  - Kiểm: `python -m pytest tests/test_claude_md_core.py tests/test_doc_index.py tests/test_token_budget.py -q`
  - Không dùng cho: Sửa đổi các file cài đặt của plugin khác ngoài TDQ Workflow

- [x] **T1.2** (e8m) Bổ sung hàm thiết lập `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` trong khối `env` của `settings.json` vào `scripts/tdq_setup.py`, tạo bản sao lưu `.tdq.bak` trước khi ghi và tôn trọng `TDQ_KHONG_CHAM_MAY=1` — Test: `python -m pytest tests/test_auto_update_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_auto_update_setup.py`
  - Cần: T1.1
  - Dùng: `claude-api`
  - Để: Đối chiếu chính xác tên biến môi trường và cơ chế idle window floor của client Claude Code
  - Ra: Hàm cấu hình timeout trong `scripts/tdq_setup.py` và test tương ứng trong `tests/test_auto_update_setup.py`
  - Kiểm: `python -m pytest tests/test_auto_update_setup.py -q`
  - Không dùng cho: Thêm SDK Anthropic API hoặc thay đổi endpoint mạng

**Xong P1 khi**: Toàn bộ tài liệu quy tắc chọn công cụ và hàm cấu hình idle timeout 90 giây đều đạt PASS trên các bài kiểm tra linter và setup.

## P2 — Cổng kiểm soát blast_radius và ngắt mạch theo workspace (O3)

- [x] **T2.1** (e12m) Bổ sung logic kiểm tra trạng thái circuit breaker từ sổ `.tdq-search.jsonl` trong `scripts/search_rules.py` (hàm thuần `trang_thai_lsp(rows)`) — Test: `python -m pytest tests/test_search_rules.py -q -k circuit`
  - Chạm: `scripts/search_rules.py`, `tests/test_search_rules.py`
  - Cần: T1.2

- [x] **T2.2** (e12m) Mở rộng matcher trong `hooks/hooks.json` và bổ sung hàm `phan_xu_blast_radius` vào `hooks/scripts/lsp_gate.py` (kiểm tra `changed_files` ≤ 3 tệp, `scope="exported"`, `include_transitive=false` và circuit breaker) — Test: `python -m pytest tests/test_lsp_gate.py -q`
  - Chạm: `hooks/hooks.json`, `hooks/scripts/lsp_gate.py`, `tests/test_lsp_gate.py`
  - Cần: T2.1

**Xong P2 khi**: `tests/test_lsp_gate.py` và các ca kiểm tra circuit breaker trong `test_search_rules.py` đạt 100% PASS (chặn đúng khi vượt ngưỡng hoặc khi mạch mở; cho phép khi hợp lệ và mạch đóng).

## P3 — Sổ quan sát thời gian chạy và phân loại kết quả LSP (O4)

- [x] **T3.1** (e10m) Bổ sung hàm thuần `phan_loai_ket_qua_lsp(su_kien, payload)` trong `scripts/search_rules.py` để phân loại 4 nhãn `outcome` (`ok`, `empty`, `error`, `timeout`) — Test: `python -m pytest tests/test_search_rules.py -q -k outcome`
  - Chạm: `scripts/search_rules.py`, `tests/test_search_rules.py`
  - Cần: T2.2

- [x] **T3.2** (e12m) Đăng ký `PostToolUseFailure` cho `mcp__lsp__.*` trong `hooks/hooks.json` và cập nhật `hooks/scripts/search_observe.py` để ghép cặp `PreToolUse` với `PostToolUse`/`PostToolUseFailure`, tính `duration_ms` và ghi dòng `lsp_ket_qua` mà vẫn bảo toàn 100% mở khóa `khai_niem` — Test: `python -m pytest tests/test_search_observe.py -q`
  - Chạm: `hooks/hooks.json`, `hooks/scripts/search_observe.py`, `tests/test_search_observe.py`, `README.md`, `tests/test_subagent_start.py`
  - Cần: T3.1

**Xong P3 khi**: `tests/test_search_observe.py` đạt 100% PASS, kiểm chứng được dòng `lsp_ket_qua` có `duration_ms`, 4 trạng thái `outcome` và không làm gãy hợp đồng mở khóa `khai_niem` ở `PreToolUse`.

## P4 — Thống kê p50/p95 và đối chiếu độ phủ caller oracle (O5)

- [x] **T4.1** (e12m) Bổ sung các hàm thuần `thong_ke_lsp(rows)` và `doi_chieu_caller_oracle(tap_tim_thay, tap_chuan)` trong `scripts/search_rules.py` — Test: `python -m pytest tests/test_search_rules.py -q -k oracle`
  - Chạm: `scripts/search_rules.py`, `tests/test_search_rules.py`
  - Cần: T3.2

- [x] **T4.2** (e12m) Mở rộng `scripts/search_replay.py` hỗ trợ ghép cặp `tool_use`/`tool_result` từ transcript JSONL và bổ sung cờ `--lsp-telemetry` xuất báo cáo p50/p95, outcome và caller oracle — Test: `python -m pytest tests/test_search_replay.py -q`
  - Chạm: `scripts/search_replay.py`, `tests/test_search_replay.py`
  - Cần: T4.1

**Xong P4 khi**: `tests/test_search_replay.py` và `tests/test_search_rules.py` đạt 100% PASS, xuất được bảng đo p50/p95 và tỷ lệ độ phủ caller.

## Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)

- Đã khai báo chi tiết ở từng task phía trên: `skills/tdq-setup/references/uu-tien-tim-kiem*.md`, `scripts/tdq_setup.py`, `hooks/hooks.json`, `hooks/scripts/lsp_gate.py`, `hooks/scripts/search_observe.py`, `scripts/search_rules.py`, `scripts/search_replay.py` và các bài kiểm thử tương ứng trong `tests/`.

## Luật file nóng (một file, nhiều task chạm)

- Các tệp `scripts/search_rules.py` và `hooks/hooks.json` được chạm ở nhiều task (T2.1/T3.1/T4.1 và T2.2/T3.2) theo nguyên tắc **một chủ ghi duy nhất**: các task được sắp xếp tuần tự theo thứ tự phụ thuộc P1 → P2 → P3 → P4, hoàn thành dứt điểm từng phần logic trước khi chuyển sang phần tiếp theo.

## Dòng `Cần:` (khai phụ thuộc giữa các task)

- Đã khai báo chi tiết ở từng task: T1.2 cần T1.1; T2.1 cần T1.2; T2.2 cần T2.1; T3.1 cần T2.2; T3.2 cần T3.1; T4.1 cần T3.2; T4.2 cần T4.1. Tuyệt đối không có phụ thuộc vòng.

## Cụm song song

- Toàn bộ chuỗi task được thiết kế tuần tự trong chế độ `main` process để bảo vệ tính nhất quán của các tệp cấu hình hook và sổ tìm kiếm, tránh xung đột ghi đè giữa các tiến trình con.

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤6 dòng)

- Đã khai báo chi tiết tại task **T1.1** (dùng `update-config`) và **T1.2** (dùng `claude-api`).

## Px — Log & test bắt buộc

- [x] **Tx.1** (e5m) Kiểm chứng log service bật mặc định (timestamp ISO trên `stderr`, chi tiết debug, tắt được bằng `TDQ_LOG=0`) trên `lsp_gate.py`, `search_observe.py`, `search_rules.py` và `search_replay.py` — Test: `python -m pytest tests/test_lsp_gate.py tests/test_search_observe.py tests/test_search_replay.py -q -k log`
  - Chạm: `hooks/scripts/lsp_gate.py`, `hooks/scripts/search_observe.py`, `scripts/search_replay.py`
  - Cần: T4.2
- [x] **Tx.2** (e5m) Kiểm chứng toàn bộ suite bài kiểm thử vùng chạm của 6 nhóm chạy bằng một lệnh duy nhất — Test: `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_lsp_gate.py tests/test_search_observe.py tests/test_search_rules.py tests/test_search_replay.py -q`
  - Chạm: `tests/test_claude_md_core.py`, `tests/test_auto_update_setup.py`, `tests/test_lsp_gate.py`, `tests/test_search_observe.py`, `tests/test_search_rules.py`, `tests/test_search_replay.py`
  - Cần: Tx.1

## Definition of Done

Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm, MỖI DÒNG MỘT Ô TICK:

- [x] Q1 Đồng bộ chính sách chọn công cụ 3 tầng và trung hòa chỉ thị `blast_radius` (O1) — `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md; python scripts/token_budget.py --kiem`
- [x] Q2 Thiết lập giới hạn chờ `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` 90.000 ms trong `tdq_setup.py` (O2) — `python -m pytest tests/test_auto_update_setup.py -q`
- [x] Q3 Kiểm soát phạm vi `blast_radius` (≤ 3 tệp, `exported`, không bắc cầu) và circuit breaker tại `lsp_gate.py` (O3) — `python -m pytest tests/test_lsp_gate.py tests/test_search_rules.py -q -k circuit`
- [x] Q4 Quan sát thời gian chạy và phân loại kết quả tại `search_observe.py` (O4) — `python -m pytest tests/test_search_observe.py -q`
- [x] Q5 Thống kê p50/p95 và đối chiếu độ phủ caller chuẩn trong `search_rules.py` & `search_replay.py` (O5) — `python -m pytest tests/test_search_replay.py -q; python scripts/search_replay.py tests/fixtures/phien_excalidraw_tim.json --lsp-telemetry`
