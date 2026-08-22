# The check-status report shape — 6 fixed sections

`scripts/tdq_checkstatus.py report` prints exactly this shape. This file is the human-readable
version: use it to check the output carries every section, and to let an outside agent (one
that cannot run a Python script) fill it in by hand in the right order.

Six sections, in this exact order, nothing added, nothing dropped:

1. `## Request` — slug, lane, phase, mode, the opening timestamp and the last-write timestamp.
2. `## Bằng chứng trên đĩa` — a table: each asset, the plan ticks, git, the working log. <!-- i18n-allow: canonical section name printed by the detector -->
3. `## Ca lệch phát hiện` — a table of codes D1–D11, level, detail, diagnosis. <!-- i18n-allow: canonical section name printed by the detector -->
4. `## Kết luận` — exactly one of three verdicts, in bold. <!-- i18n-allow: canonical section name printed by the detector -->
5. `## Lệnh vá đề xuất` — a bash block, only the two families `set` and `approve`. <!-- i18n-allow: canonical section name printed by the detector -->
6. `## Việc kế tiếp` — exactly one sentence. <!-- i18n-allow: canonical section name printed by the detector -->

## A filled-in example (a real case: switching machines mid-`implement`)

From here to the end of the section is the detector's REAL output, copied verbatim.

<!-- i18n-allow: real detector output, quoted verbatim in the default document language -->
```markdown
# Check status — request đang dở

## Request

- Slug: `2026-08-16-1110-skill-check-status`
- Lane: full · Phase: `implement`
- Mode thực thi: main
- Mở lúc: 2026-08-16T11:11:07+07:00 · Ghi lần cuối: 2026-08-16T11:35:38+07:00

## Bằng chứng trên đĩa

| Nguồn | Thấy gì |
|---|---|
| brief | có, 117 dòng (docs/tdq/brief/2026-08-16-1110-skill-check-status.md) |
| spec | có, 165 dòng (docs/tdq/spec/2026-08-16-1110-skill-check-status.md) |
| plan | có, 225 dòng (docs/tdq/plan/2026-08-16-1110-skill-check-status.md) |
| qc | không có (docs/tdq/qc/2026-08-16-1110-skill-check-status.md) |
| reports | không có (docs/tdq/reports/2026-08-16-1110-skill-check-status.md) |
| plan tick | 15/28 xong · đang làm: T4.1 |
| git | tdq-doi-ten-mode-implement · 20 commit gần đây · 8 file bẩn |
| working log | docs/workinglog/2026-08-16.md · nhắc slug |

## Ca lệch phát hiện

| Mã | Mức | Chi tiết | Chẩn đoán |
|---|---|---|---|
| D10 | canh-bao | thiếu started_at | Mất mốc thời gian — bảng thời gian của report sẽ sai nếu không vá. |

## Kết luận

**VÁ RỒI TIẾP TỤC**

## Lệnh vá đề xuất

Chạy sau khi user gật ĐÚNG MỘT lần. Chỉ hai họ `set` và `approve`; không có lệnh nào
xoá hay ghi đè dữ liệu cũ.

    python3 scripts/tdq_state.py set started_at=ISO_MỐC_MỞ_REQUEST

## Việc kế tiếp

Làm tiếp đúng task T4.1 trong plan (task duy nhất mang `[~]`).
```

## The three verdicts

| Verdict | When | What to do |
|---|---|---|
| `TIẾP TỤC ĐƯỢC` | no case above level `ok` | report one line, then carry on <!-- i18n-allow: verdict printed verbatim --> |
| `VÁ RỒI TIẾP TỤC` | some `canh-bao`, every one of them has a patch command | ask one question, on a nod patch then continue <!-- i18n-allow: verdict printed verbatim --> |
| `CẦN USER QUYẾT` | a `chan` case, or a `canh-bao` no command can fix | stop, lay the choices out for the user <!-- i18n-allow: verdict printed verbatim --> |
