# QC — Fix dòng giải thích pipeline gây rối khi đọc lại tóm tắt

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-dong-giai-thich-lane.md · Lane: full
QC độc lập: BỎ (đã chốt trong spec §1b — việc nhỏ, thêm 1 câu quy ước/file). Tự QC bằng
đọc lại + `doc_lint.py`.

## Kết quả

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | `tdq-spec/SKILL.md` bước 4 có câu quy ước gắn nhãn khuôn mẫu | Đọc lại bước 4: có câu "cần trích nguyên khối đó làm ví dụ thì gắn nhãn rõ ngay trước đoạn trích" + nhãn mẫu "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)" | PASS |
| Q2 | `tdq-plan/SKILL.md` bước 5 có câu quy ước tương tự | Đọc lại bước 5: câu và nhãn giống hệt cách diễn đạt ở Q1, áp cho đầu ra plan | PASS |
| Q3 | `doc_lint.py` pass trên cả 2 file | `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` → exit 0 (sau khi tách câu 60/55 từ để qua R5) | PASS |

## Kết luận
3/3 PASS. DoD đạt — không còn mục QC nào FAIL, không cần thêm task fix.
