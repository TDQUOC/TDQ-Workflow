# REQUEST — Kiểm kê & tận dụng skill phụ trợ

Ngày: 2026-07-29 · Lane: **full** (user chọn) · Slug: `2026-07-29-skill-inventory`

## Nguyên văn yêu cầu

> tôi vừa restart claude r. Tôi muốn bạn check lại là tdq workflow liệu có phải là đang
> điều hướng phương thức làm khi có yêu cầu từ người dùng, khôn hạn chế các skill phụ trợ
> không? ví dụ như lam web thì mà trong skill system có skill hỗ trợ viết fontend hoặc bảo
> mật cho backend thì tdqworkflow sẽ phân tích skill đó xem có dùng được trong case này
> không? nếu được thì bổ sung vào spec/plan để claude tận dụng nó nhằm cho output tốt hơn.

> hiện tại chưa có skill phụ nhưng hãy phân tích bộ workflow và instruction để nếu chỉ 1%
> khả năng có thể dùng skill thì hãy dùng skill phụ, và đồng thời phân tích tổ chức chi tiết
> cụ thể để kể cả là một model thấp chạy local cũng hiểu rõ và làm việc đúng

Chọn lane: user nhắn `1` = lane full (spec → duyệt → plan → duyệt → build).

## Cách hiểu đầu tiên

Hai mục tiêu tách bạch:

1. **Kiểm kê năng lực.** Workflow phải chủ động rà soát skill/agent/công cụ đang có,
   quyết định dùng hay không cho từng cái, và **ghi quyết định đó vào spec/plan** để
   subagent (context sạch) và agent ngoài (Codex/Antigravity) cũng biết mà dùng.
2. **Thiên lệch về phía DÙNG.** Chỉ cần 1% khả năng dùng được là phải dùng — nghĩa là
   mặc định khi phân vân là DÙNG, không phải BỎ QUA.
3. **Viết cho model yếu.** Câu chữ phải máy móc tới mức model nhỏ chạy local vẫn làm đúng:
   enum đóng, khuôn copy-paste, mặc định khi phân vân, điều kiện xong đo bằng artifact.

## Đã xác minh trước khi viết spec (turn phân tích)

- Không một chỗ nào trong `skills/` và `portable/` nhắc tới việc rà soát skill khác;
  năng lực ngoài duy nhất được hard-code là tavily, graphify và 3 agent nội bộ.
- Hook **không** chặn skill khác (`hooks.json` chỉ match `Edit|Write|MultiEdit|NotebookEdit`
  và `Bash`) → đây là điểm mù, không phải giới hạn kỹ thuật.
- Quét đĩa được **7** skill, thực tế context có **18** → skill built-in không nằm trên đĩa
  (`find / -maxdepth 8 -name artifact-design -type d` → rỗng).
- `find ~/.claude -name SKILL.md` cho **152** kết quả vì cache giữ mọi version cũ → cấm quét ẩu.
- `installed_plugins.json` có entry `scope: "project"` của project khác
  (`superpowers@claude-plugins-official`) → phải lọc theo `projectPath`.

## Chỗ chưa rõ

- State đang trỏ request cũ `2026-07-28-instruction-hardening-7b` (lane full, phase report).
  `init` cho request này sẽ **xoá** state đó → chờ user quyết, chưa chạy.
