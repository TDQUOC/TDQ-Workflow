# Tiết kiệm context

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context: output `n` ký tự tốn
`n/4 × số API call còn lại` — **carry-cost**. Đo bằng:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/token_audit.py" --sessions 2 --top 8
```

- **Gộp tool call.** Biết trước 2–5 tool call độc lập (Bash, Read, Grep) → phát hết
  trong CÙNG MỘT LƯỢT; nhiều lệnh Bash độc lập thì gộp bằng `&&`. Tách khi cần khoanh vùng lỗi.
- **Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục
  (`docs/tdq`): lint thư mục in ~8.000 ký tự lỗi của file cũ, không liên quan.
- **CLI im lặng.** `tdq_state.py init|set|reset` mặc định in 1 dòng; chỉ thêm `--json`
  khi thật sự cần soi state. `next --brief` thay cho `next` trừ khi cần checklist đầy đủ.
- **Đọc vừa đủ.** File trên 200 dòng: `grep -n` định vị rồi Read theo `offset`/`limit`.
  Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời.
- **Việc nặng giao subagent.** Research web và đọc ≥4 file giao agent riêng — agent có
  context window riêng, chỉ trả digest về hội thoại chính.
