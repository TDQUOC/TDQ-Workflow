# Xử lý 10 issue nền và lỗi khóa file kiểm thử {#spec-ba}

**Đồng bộ quy chuẩn 11 skills, nâng trần description 2.150 ký tự, nạp UTF-8 cho 5 entrypoints và chuẩn hóa 4 bộ test trên Windows.**

- Nhóm 1 (Entrypoints UTF-8): Nạp `utf8_io` / `_common` cho 5 script và hook.
- Nhóm 2 (Cấu trúc & Ngân sách Skill): Khai báo đủ 11 skills trong `SKILL_LINE_LIMITS`, nâng trần description lên 2.150, nối link tầng 1 và sửa link chết.
- Nhóm 3 (Kiểm thử Hợp đồng & Windows): Sửa fixture phase `implement`, chuẩn hóa ngưỡng bán kính, tách đường dẫn có nháy kép và thử lại khi xóa tệp tạm bị khóa.

@answer scope="Thiết kế v1.0 · chờ duyệt · Mức QC ultra"
@meta locale=en style=editorial

## Luồng thực thi 3 nhóm sửa lỗi {#flow}

@workflow id=fix-flow title="Thứ tự triển khai sửa 11 điểm lỗi"
| utf8 | Nạp UTF-8 | backend |
| skills | 11 Skills | backend |
| tests | 4 Bộ Test | security |
| qc | QC Ultra | security |
| utf8 > skills | UTF-8 |
| skills > tests | chỉ mục |
| tests > qc | PASS | emphasis |

| Nhóm | Hạng mục xử lý | Tệp đích chính |
| --- | --- | --- |
| Nhóm 1 | I06: Nạp chokepoint UTF-8 | `tdq_devtool_mcp.py`, `tdq_harvest.py`, 3 hooks |
| Nhóm 2 | I01–I05, I07: Cấu trúc, liên kết và trần 2.150 ký tự | `doc_lint.py`, 5 `SKILL.md`, `spec-template.md`, `test_token_budget.py` |
| Nhóm 3 | I08–I10 + WinError 32: Hợp đồng & khóa tệp Windows | `test_reminder_contract.py`, `test_tdq_test.py`, `test_tuong_thich_host.py`, `test_tu_khoi_tao.py` |
