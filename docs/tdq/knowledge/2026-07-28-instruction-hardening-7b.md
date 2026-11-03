# KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)

Ngày: 2026-07-28 · Nguồn: [request](../requests/2026-07-28-instruction-hardening-7b.md) · [questions](../questions/2026-07-28-instruction-hardening-7b.md) · [research](../research/2026-07-28-instruction-hardening-7b.md)

## 1. Vấn đề cốt lõi

0.2.0 đã bỏ gate cứng, nhưng thay thế bằng **chữ**: hook nhắc, skill dặn, CLAUDE.md dặn — không có gì kiểm được là agent có làm theo hay không. Research xác nhận đây là điểm yếu đã biết của cả hệ sinh thái: instruction là "wish list, not a contract"; càng nhiều rule tỉ lệ tuân thủ càng giảm. Muốn ổn định tới mức model yếu cũng đi đúng thì phải **giảm lượng chữ phải suy luận** và **tăng lượng việc có thể chạy bằng lệnh**.

## 2. Quyết định đã chốt

| # | Quyết định | Lý do |
|---|---|---|
| K1 | Hook giữ nguyên vai trò nhắc (`allow` + `additionalContext`), không quay lại `deny` | Cơ chế hợp lệ (doc chính thức xác nhận PreToolUse nhận `additionalContext`); user đã chọn hướng này ở 0.2.0 |
| K2 | Mỗi lời nhắc mang **mã lệnh ngắn** (`[TDQ:LOG]`, `[TDQ:APPROVE]`, `[TDQ:PLAN]`…) và agent phải **echo 1 dòng xác nhận** đã xử lý | Biến việc tuân thủ thành thứ **kiểm chứng được** trong transcript, thay vì niềm tin |
| K3 | `stop_gate` soát transcript: có mã nhắc mà không có dòng echo tương ứng → nhắc lại cuối turn (`additionalContext` của Stop, hoặc block nếu là working log) | Doc xác nhận Stop cũng nhận `additionalContext` → thêm một điểm nhắc mà không thêm điểm chặn |
| K4 | Thêm `tdq_state.py next` — in tiếng Việt: phase hiện tại → việc kế tiếp → lệnh copy-paste → checklist tick được | Đòn bẩy mạnh nhất cho model yếu: chuyển "suy ra bước kế tiếp" thành "chạy lệnh và đọc" |
| K5 | Gộp 9 skill → 5: `tdq-intake` (start+analyze), `tdq-spec`, `tdq-plan`, `tdq-build` (implement+qc+report), `tdq-status`; `tdq-conventions` giữ riêng làm nền | Ít điểm chuyển tiếp = ít chỗ model yếu lạc; vẫn tách theo ranh giới duyệt (spec/plan là 2 gate riêng nên không gộp) |
| K6 | Mỗi SKILL.md: thân ngắn dạng checklist đánh số + lệnh; chi tiết/ví dụ/bảng quyết định đẩy sang `references/*.md` | Chuẩn progressive disclosure của Anthropic (thân < 500 dòng); giữ token thấp mà vẫn chi tiết |
| K7 | Xoá hẳn skill `tdq-approve` | User: duyệt là câu nói tự nhiên; slash command là lớp dư |
| K8 | Sinh bản **portable** `portable/AGENTS.md` + `portable/workflow/*.md` cho harness không có hook/skill; logic chung dồn vào `tdq_state.py` | User muốn chạy được cả ngoài Claude Code; script là phần duy nhất chạy được ở mọi nơi |
| K9 | Nghiệm thu bằng **lint doc tự viết** chạy trong `tests/`; không tải model 7B | Đo được, lặp lại được, không phụ thuộc download |
| K10 | Gộp toàn bộ mục rà soát T2–T4, C1–C5, D1–D2 vào request này | Cùng chạm một nhóm file |
| K11 | Sửa `~/.claude/CLAUDE.md` §10 cho khớp 0.3.0, trình nội dung trước khi ghi đè | User cho phép |

## 3. Tiêu chí "model yếu đọc cũng làm đúng" (lint sẽ chấm)

Rút từ research R3+R4, sẽ thành rule của script lint:
1. Mỗi bước = **một hành động**, có số thứ tự.
2. Bước nào có thao tác hệ thống thì phải kèm **lệnh copy-paste được** (trong khối ``` ).
3. Có **điều kiện vào/ra** rõ ràng ("Xong khi …", "Nếu … thì sang bước N").
4. Cấm từ mơ hồ trong phần bắt buộc: "nếu cần", "tùy", "có thể", "nên cân nhắc" — hoặc phải kèm bảng quyết định.
5. Thể mệnh lệnh, câu ngắn.
6. Thân SKILL.md < 500 dòng; phần dài nằm ở `references/`.
7. Format output tường minh khi skill sinh văn bản (spec/plan/report có mẫu).

## 4. Đánh đổi đã biết

- Đổi tên skill → slash command cũ mất; phải cập nhật `~/.claude/CLAUDE.md`, README, `docs/notes/user-level-install.md` cùng lượt.
- Echo bắt buộc làm câu trả lời dài thêm vài dòng mỗi turn — chấp nhận để có dấu vết.
- Lint doc không chứng minh model 7B thật sự chạy đúng; nó chỉ chứng minh doc đạt tiêu chí. Ghi rõ giới hạn này trong report.
- `next` là nguồn sự thật thứ hai bên cạnh skill → phải có test chống lệch giữa hai bên.

## 5. Chưa quyết (không chặn spec)

- Có thêm `--json` cho `next` hay không → để version sau nếu harness khác cần.
