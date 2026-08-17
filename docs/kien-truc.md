# Hồ sơ kiến trúc — TDQ Workflow

Trạng thái: **NHÁP — chờ user chốt** (sinh 2026-08-15 trong phase analyze của request
`2026-08-15-toi-uu-thoi-gian-phase`). Chưa chốt thì mọi dòng ở đây là gợi ý, không phải luật.

Nguồn sinh: cây thư mục repo · `graphify god-nodes` · `.graphifyignore`.

## Tầng

| Tầng | Thư mục | Trách nhiệm |
|---|---|---|
| Luật | `skills/` | văn bản chỉ dẫn model; không chạy được, không có trạng thái |
| Luật bản ngoài | `portable_claude/`, `portable_codex/` | SINH bằng `scripts/build_portable.py` từ `skills/`+`hooks/`+`agents/`+`scripts/`, không sửa tay; bản codex dùng lớp native của Codex CLI (`.agents/skills/`, `.codex/`) |
| CLI | `scripts/` | mọi hành vi chạy được: state, kết turn, lint, quét rule, đo token |
| Hook | `hooks/scripts/` | 5 hook cắm vào Claude Code, nhắc mã `[TDQ:*]` và chặn khi thiếu bằng chứng |
| Test | `tests/` | khoá hành vi của tầng CLI, tầng hook và tính nhất quán của tầng luật |
| Dữ liệu request | `docs/tdq/` | brief, spec, plan, qc, report, state — dữ liệu, không phải code |

## Luật gọi

- `hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/` — hook chạy trong
  tiến trình của Claude Code, kéo ngược sẽ buộc CLI phụ thuộc môi trường hook.
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill —
  hai bản chép tay sẽ lệch nhau và không có phép kiểm nào bắt được.
- Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI.
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — thư mục khác bị
  `.graphifyignore` loại nên đồ thị không thấy.
- `tests/` gọi được vào mọi tầng; không tầng nào được import `tests/`.

## Hub

5 node nhiều liên kết nhất (`graphify god-nodes`) — sửa các node này là rủi ro cao, phải
khai ở dòng `Chạm:` của plan:

| # | Node | Số bậc |
|---|---|---|
| 1 | `Changelog` | 28 |
| 2 | `main()` | 20 |
| 3 | `cli()` | 17 |
| 4 | `log()` | 17 |
| 5 | `cmd_build()` | 17 |

## Đã chốt

- 2026-07-29: gom 10 skill còn 6; bỏ hẳn skill duyệt, duyệt bằng chat thường.
- 2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do "chưa duyệt".
- 2026-08-13: `CHANGELOG.md` giữ dưới trần 500 dòng của `doc_lint` R6; phần cũ xoay vào
  `docs/archive/CHANGELOG-*.md`.
- 2026-08-14: `skills/tdq-conventions/references/soul.md` là luật gốc đứng trên mọi luật;
  đổi soul phải có user duyệt.
