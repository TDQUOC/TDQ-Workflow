# Research — 2026-08-04-approval-gate-bug

## Truy vấn 1: Claude Code PreToolUse hook permissionDecision deny — chặn cứng theo pattern nào
- Nguồn: kết quả tavily-primary chủ yếu không liên quan trực tiếp (trang giới thiệu Claude
  chung chung). Không có bài viết chuyên sâu về pattern chặn cứng PreToolUse công khai.
- Rút ra: không có tài liệu ngoài mô tả cụ thể cách side "deny" một Bash call theo điều
  kiện — nhưng cơ chế `hookSpecificOutput.permissionDecision: "deny"` đã có sẵn trong chính
  Claude Code (đã dùng ở `edit_gate.py`/`bash_gate.py` hiện tại cho `allow`, chưa dùng
  `deny` bao giờ trong plugin này) — đủ để tự thiết kế mà không cần thêm nguồn ngoài.

## Truy vấn 2: LLM agent bỏ qua instruction chèn trong context / tool output — failure mode
- Nguồn: arxiv.org/html/2503.13657v2 ("Why Do Multi-Agent LLM Systems Fail?", MAST taxonomy).
- Rút ra: "fail to follow task requirements" là failure mode phổ biến (~11%) xếp vào nhóm
  lỗi THIẾT KẾ HỆ THỐNG (kiến trúc/prompt/state management), không phải lỗi hiếm gặp của
  riêng một model. Tài liệu khuyến nghị fix ở tầng kiến trúc (workflow/state management),
  không chỉ ở tầng prompt — khớp với hiện trạng: `approval.md` (tầng prompt) đã tồn tại
  từ lâu nhưng vẫn tái diễn lỗi, nghĩa là cần thêm tầng kiến trúc/state.

## Truy vấn 3: Human-in-the-loop approval gate — chặn cứng vs nhắc mềm
- Nguồn: stackai.com "Human-in-the-Loop AI Agents: Approval Workflows".
- Rút ra: nguyên tắc thiết kế cốt lõi được nhắc lại nhất quán ở nhiều nguồn — **tách rời
  Ý ĐỊNH (agent đề xuất) khỏi THỰC THI (hệ thống thực thi)**: agent được phép suy luận tự
  do, nhưng việc THỰC THI bị chặn bởi state transition tường minh nằm NGOÀI khả năng tự ý
  của agent. Áp vào ca này: bước "ghi nhận đã duyệt" (`tdq_state.py approve`) chính là
  điểm THỰC THI cần tách khỏi phán đoán của Claude — hiện tại Claude vừa là bên đề xuất
  (đọc `approval.md`, tự phán) vừa là bên thực thi (tự chạy lệnh `approve`), không có lớp
  nào độc lập xác nhận điều kiện trước khi cho thực thi.

## Đối chiếu với lịch sử chính plugin (đọc code, không phải research ngoài nhưng liên quan)
- `git log`: plugin **đã từng có** một hard gate slash-command (`approve_gate`, v0.1.4–0.1.6)
  bị bỏ ở v0.3.0 ("bỏ approve_gate; stop_gate verify-by-effect qua turn ledger"). Lý do bỏ
  (suy từ code + docstring `stop_gate.py`): gate cũ đọc **transcript** để tìm dòng mời duyệt
  cuối cùng — cách này từng gây bug ở v0.1.8 (chặn nhầm/bỏ sót). Kiến trúc mới ("verify-by-
  effect") cố tình tránh đọc transcript, chỉ tin dữ liệu quan sát được trực tiếp (turn
  ledger, snapshot đĩa).
- Tuy nhiên `prompt_context.py` (thêm sau, không rõ version) đã có sẵn hàm
  `looks_like_approval()` — một bộ nhận diện CÓ ĐỘ TIN CẬY CAO vì đọc trực tiếp
  `payload["prompt"]` của `UserPromptSubmit` (dữ liệu thô, không qua transcript) — cùng lớp
  tin cậy với turn ledger/snapshot mà kiến trúc 0.3.0 đã chấp nhận. Hiện hàm này CHỈ dùng để
  IN GỢI Ý (`additionalContext`), không có gì bắt buộc Claude phải tuân theo — `bash_gate.py`
  không hề tra cứu lại tín hiệu này khi thấy Bash gọi `tdq_state.py approve`.

## Kết luận rút ra cho hướng kỹ thuật
Có sẵn đúng một tín hiệu đáng tin cậy (không phải transcript) để chặn cứng: kết quả
`looks_like_approval()` tính lúc `UserPromptSubmit`. Việc còn thiếu là (a) LƯU tín hiệu đó
vào sổ turn, và (b) THÊM một điều kiện `deny` trong `bash_gate.py` khi phát hiện lệnh
`tdq_state.py approve <target>` (hoặc `set phase=...` tương ứng) mà tín hiệu turn hiện tại
không phải "đã duyệt". Cách này tái dùng đúng loại kiến trúc "verify bằng dữ liệu quan sát
trực tiếp" mà 0.3.0 đã chọn, không lặp lại lỗi transcript-reading của gate cũ đã bị bỏ.
