# portable/ — dùng TDQ workflow ngoài Claude Code

Bản dịch tay của `skills/tdq-*` cho harness không có hook/skill system (Codex,
Antigravity, …). **Không tự sinh** — sửa `skills/` xong nhớ đồng bộ tay các file ở đây,
đặc biệt `workflow/phases.md` (sinh lại bằng lệnh ở dưới).

## Copy sang project đích

Copy đúng 3 thứ vào root project đích:

```bash
cp path/to/TDQWorkflow/portable/AGENTS.md      /project-đích/AGENTS.md
cp -r path/to/TDQWorkflow/portable/workflow    /project-đích/workflow
cp path/to/TDQWorkflow/scripts/tdq_state.py    /project-đích/scripts/tdq_state.py
```

Kiểm: trong project đích chạy `python3 scripts/tdq_state.py next` → phải in
"Chưa có request TDQ nào đang chạy…" (chưa có `docs/tdq/state.json`).

## Đồng bộ khi `skills/` đổi

`portable/` không có test tự động khoá đồng bộ (bản cũ từng có
`tests/test_portable_sync.py`, đã xoá cùng lần dọn mode `external` ở 0.10.0). Sau khi
sửa bất kỳ file nào trong `skills/tdq-{conventions,intake,spec,plan,build}/`, kiểm lại
xem `portable/` có cần sửa theo không — nhất là khi đổi `PHASE_TABLE`,
`VALID_MODES`, luật QC quick, hay khuôn plan/spec.

Sinh lại `workflow/phases.md` sau mỗi lần đổi `PHASE_TABLE` trong `scripts/tdq_state.py`:

```bash
python3 scripts/tdq_state.py phases-doc > portable/workflow/phases.md
```

## Khác biệt so với plugin Claude Code

Không có hook nhắc `[TDQ:*]`, không có `tdq_finish.py` gộp việc, không có sub-agent
chuyên biệt sẵn. Xem mục "Không có ở bản portable này" cuối `AGENTS.md`.
