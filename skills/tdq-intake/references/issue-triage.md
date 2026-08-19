# Xử lý issue/lỗi do user báo

Applies when the new request is a **bug report** rather than a feature: "chạy sai",
"bị treo", "kết quả không như mong đợi". The goal of triage is enough evidence to write a
fix spec — never a guess.

## Thứ tự bắt buộc

1. **Read the log first.** No proposed cause before you have looked at a log. Where logs
   live: the product's own log service, `docs/workinglog/<ngày>.md`, the latest test
   output, the previous session transcript in `~/.claude/projects/<project>/`.
2. **Reproduce.** Run the exact command the user ran. Cannot reproduce → ask the user for
   the command, input, version and environment before going any further.
3. **Capture when the bug is at the UI layer.** If computer use is needed to record the
   flow, save the capture into a temp folder **inside the repo**, with one note line giving
   the time and the reproduction steps. Delete the capture once the issue is closed.
4. **Frame the problem.** Write down: symptom · where it surfaces (file:dòng) · trigger
   condition · blast radius. Any box missing → back to step 1.
5. **Research the fix.** Search by the verbatim error and by library name + version. Rule
   for calling search: [tavily.md](../../tdq-conventions/references/tavily.md).
6. **Settle the evidence before writing the spec.** A fix spec must state the root cause,
   the fix, and a test that reproduces the bug (red before the fix).

## Sai lầm hay gặp

| Sai | Đúng |
|---|---|
| Sửa theo triệu chứng | Tìm nguyên nhân gốc rồi mới sửa |
| Sửa xong không có test | Viết test tái hiện lỗi, đỏ → xanh |
| Đoán nguyên nhân vì không có log | Bật log chi tiết, chạy lại, đọc log |
| Xoá capture/log ngay | Giữ đến khi issue đóng, ghi trong report |
