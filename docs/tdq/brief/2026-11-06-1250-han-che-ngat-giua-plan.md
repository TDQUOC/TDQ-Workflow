# Brief — Hạn chế ngắt giữa plan
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay mở request update bổ sung vào tdq-workflow để hạn chế nhất có thể tình trạng ngắt giữa plan

Đọc lần đầu: cập nhật TDQ-Workflow giảm tình trạng model (nhất là model nhỏ) ngừng khi plan chưa hoàn tất. Ưu tiên bám plan, khi lệch nhỏ thì đối chiếu spec, ghi lệch và tiếp tục; giữ cổng duyệt, bốn lý do pause, tránh lặp vô hạn hoặc chạy trùng. Người dùng chọn **chỉ Claude Code** (`1b`); không thêm watchdog ngoài session, không sửa Antigravity. Hook không phát sự kiện giữa lúc API/tool đang treo: phạm vi lần này là dừng sớm ở ranh giới Stop và khôi phục khi resume. Chưa sửa mã.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Phán quyết | Lý do |
|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | NỀN | Pipeline deep, duyệt spec/plan, red→green và QC. |
| LSP, Graphify, Grep | DÙNG | LSP tham chiếu `unfinished_reason` (11 vị trí); Graphify affected `plan_tick_state` ra Stop, SessionStart, prompt_context; Grep thấy test và host thứ hai. |
| `tdq-lean` | DÙNG | Rà diff tránh thêm scheduler/hệ thống thừa. |
| `tdq-browser-research`, `tdq-browser-test` | KHÔNG — khác lĩnh vực | Không sửa UI/web. |
| `/goal`, `/loop` | KHÔNG — tăng phí/không đúng vị trí | `/goal` dùng model đánh giá khác, cần chủ động bật ở session; `/loop` chỉ nổ khi session rảnh, không can thiệp lời gọi đang treo. |

### Bảng đối chiếu vùng chạm

| Vùng file chạm | Phát hiện | Tác động & quan hệ |
|---|---|---|
| `hooks/scripts/stop_gate.py:154-229` | Grep, LSP `unfinished_reason` (11 refs), Graphify từ `plan_tick_state` | Đã chặn Stop 3 lần cho phase `implement` còn task; sau đó chỉ nhắc `[TDQ:STUCK]`. Không chặn khi đã pause, thiếu plan, task đã giao. Trần 300 ký tự. |
| `hooks/scripts/session_start.py:295-337`, `hooks/scripts/prompt_context.py:249-379` | Grep + Graphify affected `plan_tick_state` | Anchor ở resume/compact ghi `doing`, `dispatched` nhưng không nói task nào cần làm tiếp; prompt đầu lượt gọi `render_next`, có thể nêu tiếp task còn mở mà không đổi state. |
| `skills/tdq-build/SKILL.md:19-40`, `skills/tdq-build/references/qc.md`, `skills/tdq-conventions/references/phases.md` | Grep | Đã có luật giữ một turn, `lech add` và phương án dự phòng; cần nhấn mạnh ưu tiên plan→spec, commit chỉ để gỡ blocker, không tự dừng vì lệch nhỏ. |
| `tests/test_stop_gate.py:718-855`, test SessionStart/PromptContext và contract | Grep | Test khóa: 3 block rồi hạ cấp, reset khi tick; giữ ca không plan/pause/dispatched/phase khác. Test mới cần chứng minh lời nhắc đúng task + không lặp vô hạn. |
| `hooks/scripts/agy_stop_gate.py:133-206` | Grep | Bản port cùng logic nhưng user đã loại Antigravity khỏi phạm vi: không sửa, ghi rõ hành vi khác host. |

### Kết luận kỹ thuật

- Theo tài liệu chính thức [Hooks](https://code.claude.com/docs/en/hooks), Stop chỉ chạy khi Claude kết thúc lượt, SessionStart chạy khi resume/compact. Không hook nào theo dõi lời gọi API im giữa lượt. [Hooks guide](https://code.claude.com/docs/en/hooks-guide.md#stop-hook-hits-the-block-cap) nêu Claude Code tự hạ Stop hook sau 8 lần chặn liên tiếp mà không có tool call; tăng `MAX_STREAK` vô hạn không chữa model lặp.
- [Goal](https://code.claude.com/docs/en/goal) là cơ chế session-scoped tự lặp có model đánh giá và phí riêng; không tự bật, không thêm watchdog/cron theo phạm vi đã chốt.
- Đã có trần nội bộ 3 lần; cải thiện tối thiểu: sau trần đưa chẩn đoán cụ thể vào reminder, và làm rõ khôi phục trên lượt mới. Không tự khởi chạy lại tool, không xóa trần, không đổi bốn loại `pause` hay cổng duyệt.
- Research ngoài đã làm qua URL tài liệu chính thức, không cần thêm dịch vụ nghiên cứu. Kiến trúc `docs/kien-truc.md` vẫn NHÁP; giữ luật gọi hook→script và chỉ CLI ghi state, không thêm state writer.

### Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Analyze → spec → plan → implement → QC → report | CÓ | Thay đổi Stop hook ảnh hưởng mọi request; cần duyệt hai cổng, test trước/sau và report. |
| Research chính thức | CÓ — đã làm | Xác thực ranh giới Stop/SessionStart, giới hạn block host. |
| `/goal`, `/loop`, watchdog, Antigravity | BỎ | Ngoài phạm vi đã chọn; không tự tiêu phí model hay chạy trùng. |
| QC agent độc lập | BỎ | Người dùng chọn `full`, không phải `ultra`. |

## Hỏi đáp

1. Phạm vi → **chỉ Claude Code**; không sửa Antigravity/watchdog ngoài session (`1b`).
2. Sau 3 lần không tiến triển → **hạ cấp và báo kẹt**, kèm task/bước cần kiểm; không chặn vô hạn, không retry tool (`1a`).
3. Lệch nhỏ → **đối chiếu spec, ghi `lech add` rồi tiếp tục**, chỉ commit khi gỡ blocker; không đổi đầu ra/quyền hoặc bỏ kiểm an toàn; gom duyệt ở report (`2a`).
4. QC → **full** (`3a`), state đã ghi `muc_qc=full`.
5. Bổ sung `/goal` → **có xác nhận** (`1a` ở vòng góp ý spec): TDQ đưa điều kiện hoàn thành plan/DoD/QC để người dùng chủ động bật trong session; không tự bật, không gọi model đánh giá nếu chưa bật. Đây không phải lời duyệt spec.
6. Scope round chi tiết bỏ vì lựa chọn host `1b` đã chốt đầu vào và vùng chạm; không cài đặt hay gọi model trả phí khi chưa bật goal.
