# Benchmark A/B — Graphify code-only, full và full + wiki

- Root: `TDQ-Workflow` · Cap thực: 3 full extraction · backend/model không ghi secret.
- Đây là benchmark artifact/runtime. Wiki là output derived, không được ingest ngược; vì vậy nó không tự tạo truy vấn `full_wiki` độc lập.

| Cấu hình | Kết quả | Nodes | Links | Wiki | Thời gian (ms) |
|---|---|---:|---:|---|---:|
| code_only | OK | 2472 | 5089 | False | 5083.01 |
| full | OK | 2491 | 5107 | False | 51751.43 |
| full_wiki | OK | 2483 | 5093 | True | 61888.84 |

## Quyết định selector

- Decision: **keep-current** — evidence lacks comparable retrieval/context metrics; selector stays unchanged.
- Tên chính xác: **grep**; quan hệ/kiểu/rename: **LSP**; khái niệm/kiến trúc: **Graphify + grep, then verify**.
- Không có P/R/F1 hoặc token/tool-call claim mới: benchmark này không có gold retrieval độc lập và backend có thể không trả usage.
- Raw stdout/stderr và return code nằm trong JSONL; lỗi vẫn được giữ thay vì chuyển thành PASS.
