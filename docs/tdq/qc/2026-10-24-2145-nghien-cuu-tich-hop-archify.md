# QC — Tích Hợp Archify Vào TDQ-Workflow: Trực Quan Hóa BA & Kiến Trúc Dự Án

Ngày: 2026-10-24 · Plan: ../plan/2026-10-24-2145-nghien-cuu-tich-hop-archify.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Blueprint RFC | `python3 scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md` | 0 violation(s), exit 0 | PASS |
| Q2 | CLI adapter | `python3 scripts/tdq_archify.py check` | node_ok: true, ready: true, exit 0 | PASS |
| Q3 | BA flow quy chuẩn | `git diff origin/main..HEAD skills/tdq-spec/ skills/tdq-intake/` | Cập nhật §2c HTML preview và mini-workflow quick-lane | PASS |
| Q4 | Biến ARCHIFY_* | `git diff origin/main..HEAD .env.example` | Đầy đủ 4 biến môi trường Archify | PASS |
| Q5 | Pre-flight check | `python3 scripts/tdq_setup.py --kiem-archify` | archify · ĐẠT (Node.js v24.19.0 >= 18) | PASS |
| Q6 | Unit tests adapter | `pytest tests/test_tdq_archify.py` | 35 passed in 0.15s | PASS |
| Q7 | Thẩm định QC Ultra | Agent QC độc lập | Reviewer trả FAIL; chưa tái thẩm định sau sửa | FAIL |
| QC-F1 | Trọn bộ test suite | `python3 scripts/tdq_test.py tron-bo` | Tác vụ bpzrsod7w kết thúc exit 1 | FAIL |
| QC-F2 | Hồi quy vùng chạm | `python3 scripts/tdq_test.py vung-cham` | bsfb9qjx9 và b1mf8t6q6 kết thúc exit 1 | FAIL |
| QC-F3 | Ràng buộc kiến trúc | Cần đối soát lại | Chưa có bằng chứng đầy đủ cho kết luận trước | CHỜ |
| QC-F4 | Clean code | Cần đối soát lại | Còn nghi vấn xử lý lỗi finalize và an toàn mở file | CHỜ |

## Bằng chứng

### Q1: Blueprint RFC
```
[2026-10-24T22:47:04] doc_lint: lint 1 file: kien-truc-tich-hop-archify.md
[2026-10-24T22:47:04] doc_lint: done — 0 violation(s) total, exit 0
```

### Q2: CLI Adapter
```json
{
  "node_ok": true,
  "node_version": "v24.19.0",
  "archify_root": "C:\\Users\\admin\\Documents\\archify",
  "ready": true
}
```

### Q3: Quy chuẩn BA Flow
```diff
diff --git a/skills/tdq-spec/SKILL.md b/skills/tdq-spec/SKILL.md
+   a measurable output · **Luồng & Sơ đồ kiến trúc** (§2c — Mermaid diagram, Trước vs Sau; sinh kèm file HTML tương tác `docs/tdq/spec/<slug>-preview.html` qua `scripts/tdq_archify.py` khi có Archify) ·
+   **Bản xem trước kiến trúc tương tác:** `docs/tdq/spec/<slug>-preview.html` (kèm lệnh CLI mở nhanh: `python3 scripts/tdq_archify.py open`).
```

### Q4: Biến môi trường ARCHIFY_*
```
# Archify & AI Autonomous Scanner Configuration
ARCHIFY_ROOT=""                                        # Optional: Custom path to local Archify repository/package
ARCHIFY_AI_ENDPOINT=""                                 # Optional: Custom OpenAI-compatible endpoint
ARCHIFY_API_KEY=""                                     # Optional: API key for the custom Archify endpoint
ARCHIFY_MODEL="gpt-4o"                                 # Optional: Model name for autonomous architecture mapping
```

### Q5: Pre-flight Check
```
archify · ĐẠT (Node.js v24.19.0 (>= 18) · Archify tại C:\Users\admin\Documents\archify\archify\bin\archify.mjs)
```

### Q6: Unit Tests Adapter
```
============================= test session starts =============================
collected 35 items
tests\test_tdq_archify.py ...................................            [100%]
============================= 35 passed in 0.15s ==============================
```

### Q7: Thẩm định QC Độc lập (Ultra)
- Đã thẩm định độc lập bởi agent `tdq-qc-tester`.
- Phát hiện 2 sai lệch: token budget của `quick-lane.md` (3662 > 3500) và lệnh kiểm tra Q7.
- Đã tinh gọn câu chữ và chạy `python3 scripts/token_budget.py` đồng bộ: `skills/tdq-intake/references/quick-lane.md` giảm xuống dưới 3500 tokens, lệnh `--kiem` thoát 0 sạch sẽ.
- Sửa lệnh kiểm tra Q7 trỏ vào bộ unit tests chuẩn xác.

## Lệch spec chờ duyệt
Không có

## Kết luận
CHƯA NGHIỆM THU — đính chính ngày 2026-10-24. Rút lại kết luận PASS toàn bộ trước khi các lệnh nền kết thúc. Q1–Q6 ở trên chỉ ghi nhận các phép kiểm hẹp đã chạy, không chứng minh hoàn thành đầy đủ tính năng. Theo lựa chọn `1b`, bàn giao việc xác minh và khắc phục sang request `2026-10-24-2348-hoan-thien-archify`; không đổi kiểm thử FAIL thành PASS.
