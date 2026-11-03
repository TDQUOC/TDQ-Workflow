# QC — Rà quốc tế hoá cổng duyệt/góp ý
Ngày: 2026-08-21 · Plan: ../plan/2026-08-21-2311-workflow-da-ngon-ngu.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | 12 mã có phán quyết, không câu "chưa rõ" | `grep -c "^Phán quyết: " <audit>` · `grep -c "chưa rõ" <audit>` | 12 · 0 | PASS |
| Q2 | bằng chứng trích lại được | `sed -n '<dòng>p' <file>` cho 6 mốc `file:dòng` | cả 6 khớp nội dung ghi trong tài liệu | PASS |
| Q3 | mỗi mã CHƯA đúng một đề xuất | đếm `CHƯA` ở bảng tổng · `grep -c "^### Đề xuất"` | 8 · 8 | PASS |
| Q4 | đề xuất giữ tương thích ngược | `grep -c "^Tương thích ngược:"` | 8 = số khối đề xuất | PASS |
| Q5 | không ghi ra ngoài `docs/tdq/` | `git status --short` | mọi mục ngoài `docs/tdq/` đều đã có trong mốc T1.1 | PASS |
| Q6 | suite y hệt mốc | `python3 -m pytest tests/ -q` | 37 failed · 1166 passed · 1369 subtests, 87,07s — bằng mốc | PASS |
| Q7 | lượt phản chứng đủ 12 mã | `grep -c "^Phản chứng: " <audit>` | 12 | PASS |
| Q8 | lint sạch | `doc_lint --pair <spec> <plan>` · `doc_lint <audit>` | exit 0 · exit 0 (0 vi phạm) | PASS |
| QC-F1 | full suite | như Q6 | 37 failed / 1166 passed — 37 lỗi đều ở `tests/test_skill_router.py`, có từ trước request | PASS (bằng mốc) |
| QC-F2 | hồi quy vùng chạm | plan không có dòng `Chạm:` nào (task tài liệu) | KHÔNG ÁP DỤNG — không sửa file mã nguồn | PASS |
| QC-F3 | ràng buộc kiến trúc spec §5 | `git status --short` + đọc lại 3 dòng luật gọi | không sửa `hooks/`, `scripts/`, `skills/` nên không dòng nào bị chạm | PASS |
| QC-F4 | clean code | — | KHÔNG ÁP DỤNG — không sửa file code | PASS |

## Bằng chứng

### Q1 / Q7
```
Q1a=12 Q1b=0
Q7=12
```

### Q2 — 6 mốc trích ngẫu nhiên
```
prompt_context.py:31  AGREE = re.compile(r"\b(duyệt|duyet|ok|oke|okay|đồng\s*ý|don…
prompt_context.py:50  LETTER = re.compile(r"^\s*(?:chọn\s+|chon\s+)?([ab])\b\s*(?:…
_common.py:183        return f"➤ Duyệt: {hint} · Góp ý: nhắn trực tiếp"
tdq-conventions/SKILL.md:10  Mọi output cho user viết **tiếng Việt**.
tdq-plan/SKILL.md:80  ➤ Duyệt: nhắn "duyệt plan" (duyệt xong tôi hỏi bạn một câ…
bash_gate.py:75       if row.get("matched") is False or row.get("mode_conflict") is True
```

### Q3 / Q4
```
khối đề xuất: 8
dòng CHƯA trong bảng tổng: 8
Tương thích ngược: 8
```

### Q6 / QC-F1
```
37 failed, 1166 passed, 1369 subtests passed in 87.07s (0:01:27)
```

### Q8
```
pair=0
doc_lint: xong — tổng 0 vi phạm, exit 0
```

## Kết luận
PASS toàn bộ — 8 hạng mục DoD và 4 hạng mục cố định, không vòng fix nào.
