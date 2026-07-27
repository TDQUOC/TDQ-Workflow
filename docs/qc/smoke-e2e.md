# QC — Smoke e2e (E1) — 2026-07-27

## 1. Chain test 2 lane (hook thật, chạy subprocess)
`python3 -m unittest discover -s tests -p "test_e2e_chain.py"` → **Ran 2 tests — OK**.
- **Lane full**: init → Edit src bị deny kèm lệnh duyệt spec → ghi spec trong docs/ (được phép) + đăng ký → `tdq-approve spec` OK (sha256 + timestamp) → vẫn deny vì plan chưa duyệt → đăng ký plan → `tdq-approve plan` OK → Edit src được phép → Stop block khi log chưa cập nhật → append log → Stop im lặng.
- **Lane quick**: init quick → deny kèm lệnh duyệt quick → `tdq-approve quick` OK (message nhắc ghi workinglog) → vẫn deny vì log chưa append sau duyệt → append log (mtime > approved_at) → được phép edit.

## 2. Headless CLI thật (`claude -p --plugin-dir .`)
Chạy trên project tạm (scratchpad `smoke-proj/`):
- `claude -p "Trả lời đúng một từ: ok" --plugin-dir <repo>` → trả "ok", **EXIT=0** — plugin + 6 hook load sạch, không lỗi.
- `claude -p "/tdq-workflow:tdq-status" --plugin-dir <repo>` → trả đúng "Chưa có request TDQ nào đang chạy. Dùng tdq-start để bắt đầu.", **EXIT=0** — skill được nạp, thân skill chạy `tdq_state.py` qua `${CLAUDE_PLUGIN_ROOT}` thành công, output VI đúng thiết kế.

Giới hạn: chưa chạy full pipeline (spec→plan→implement) qua CLI thật vì cần user gõ lệnh duyệt tương tác; chuỗi đó đã được phủ bằng chain test mục 1 (gọi đúng các hook như CLI sẽ gọi).

Kết luận: **PASS**.
