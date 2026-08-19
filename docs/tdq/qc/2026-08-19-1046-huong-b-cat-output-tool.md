# QC — Hướng B: cắt output tool
Ngày: 2026-08-19 · Plan: ../plan/2026-08-19-1046-huong-b-cat-output-tool.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Thước đo đếm đúng | `pytest tests/test_token_audit.py -q`; chạy khi chặn venv | 31 passed; thiếu venv → exit 3 | PASS |
| Q2 | Bảng phân rã đủ cột | `token_audit.py --sessions 5 --top 5` | có n/trung vị/p90/p99/lớn nhất + 2 tỉ lệ Read | PASS |
| Q3 | Thước đo đủ nhanh | `/usr/bin/time -p token_audit.py --sessions 5 --top 5` | 30,6s lần chạy nguội · 5,2s lần chạy nóng | PASS |
| Q4 | Test khoá thật | chạy đỏ trước, xanh sau ở T1.1/T1.3/T1.6/T3.1/T5.1 | đủ 5 cặp đỏ→xanh | PASS |
| Q5 | Hook nhắc đúng chỗ | `pytest tests/test_bash_gate.py -q`; `grep -c '"deny"' bash_gate.py` | 22 passed; 0 chỗ có `deny` | PASS |
| Q6 | Luật không cắt chất lượng | grep `context-budget.md` | đủ 5 ca bắt buộc, còn câu "Nghi ngờ thì đọc lại", 0 chỉ tiêu % | PASS |
| Q7 | Backup hợp lệ | `md5 -q` bản backup ngoài repo | `df7ed9ce…` khớp md5 bản gốc lúc T4.1 | PASS |
| Q8 | Settings hợp lệ sau khi ghi | `json.load` lại + so khoá với backup | parse OK · khoá mới = 25000 · mất 0 khoá | PASS |
| Q9 | Ba bản đồng bộ | `build_portable.py`; `pytest tests/test_build_portable.py -q` | exit 0; 41 passed | PASS |
| Q10 | Test suite | `pytest tests -q` | 1025 passed · đỏ duy nhất là `test_skill_router` (figma), đã đỏ trước request | PASS |
| Q11 | Số trước/sau trung thực | bảng trong đề án | 3 dòng, hai mốc cùng một bộ session; phần chưa kiểm chứng ghi rõ | PASS |
| Q12 | Đề án được đính chính | `doc_lint.py de-an-toi-uu-context.md` | exit 0; mục đính chính có mặt, 12 mục cũ còn nguyên | PASS |
| F1 | Toàn bộ test suite | `pytest tests -q` | 25 failed (25 subtest của 1 test figma) · 1025 passed | PASS |
| F2 | Hồi quy vùng chạm | `pytest` 9 file test của mọi vùng `Chạm:` | 169 passed, 437 subtests | PASS |
| F3 | Ràng buộc kiến trúc | grep import + grep `deny` + `git status portable_*` | 0 import `hooks/` trong `scripts/`; 0 `deny`; portable chỉ đổi do build sinh | PASS |
| F4 | Clean code | 5 câu tự kiểm | 5/5 "có" | PASS |

## Bằng chứng

### Q1
```
31 passed, 9 subtests passed in 2.06s
exit khi thiếu venv=3
Script này CẤM ước lượng ký tự/4, nên dừng ở đây.
Cài bằng: python3 -m venv .venv-tokens && .venv-tokens/bin/pip install anthropic-tokenizer==0.1.0
```

### Q2 · Q3
```
nhóm                            lần  trung vị       p90       p99   lớn nhất
Read: 451 lần · có offset/limit 148 (32.8%) · đọc lại file đã đọc 289 (64.1%)
real 5.22          # lần chạy nóng; lần chạy nguội đầu tiên đo được 30,6s
```

### Q4 — năm cặp đỏ → xanh
```
T1.1 tokenizer thật      : 2 failed, 18 passed  → 21 passed
T1.3 bảng phân rã        : 6 failed, 21 passed  → 27 passed
T1.6 đếm ảnh theo patch  : 4 failed, 27 passed  → 31 passed
T3.1 hook TDQ:OUTPUT     : 1 failed, 21 passed  → 22 passed
T5.1 dấu vết ở 2 bản     : bỏ 1 chuỗi khỏi portable_codex → SUBFAILED; build lại → 41 passed
```

### Q5
```
22 passed in 2.29s
grep -c '"deny"' hooks/scripts/bash_gate.py → 0
```

### Q6
```
số ca đánh số trong "### Năm ca BẮT BUỘC đọc lại" → 5
"Nghi ngờ thì đọc lại" → còn nguyên
grep "chỉ tiêu|giảm N%" → rỗng
```

### Q7 · Q8
```
md5 backup ngoài repo df7ed9ced5a50d851ab796d7af752e6c (bằng md5 bản gốc lúc T4.1)
parse lại: OK · MAX_MCP_OUTPUT_TOKENS = 25000 · khoá cấp cao mất: [] · khoá env mất: []
```

### Q9 · Q10 · Q12
```
build_portable exit=0 ; tests/test_build_portable.py → 41 passed, 17 subtests
pytest tests -q → 25 failed, 1025 passed, 1241 subtests passed in 90.30s
  25 "failed" đó là 25 subtest của ĐÚNG MỘT test: test_skill_router::test_moi_duong_dan_khac_rong_deu_mo_duoc
  chứng minh đỏ sẵn có: git stash --include-untracked → vẫn 25 failed, 18 passed
doc_lint de-an-toi-uu-context.md → exit 0
```

### F2 — hồi quy vùng chạm
```
9 file test phủ mọi dòng `Chạm:` của plan (token_audit, skill_tokens, bash_gate,
context_hooks, build_portable, step_budget, luat_skill, skill_shape, reference_mot_tang)
→ 169 passed, 437 subtests passed in 31.65s
```

### F3 — ràng buộc kiến trúc
```
grep "^import hooks|from hooks" scripts/token_audit.py scripts/skill_tokens.py → 0
grep -c deny hooks/scripts/bash_gate.py → 0   (hook chỉ nhắc)
git status --short portable_* → 14 file, toàn bộ do build_portable.py sinh lại
```

### F4 — clean code, 5 câu tự kiểm
```
SRP có — dem_nhieu (đếm+cache), phan_ra (thống kê), hanh_vi_read (hành vi Read),
         dem_anh (ảnh) tách rời, mỗi hàm một lý do để đổi.
OCP có — thêm định dạng ảnh mới = thêm một hàm `_kich_thuoc_<loại>`; thêm nhóm tool
         mới = thêm dòng dữ liệu trong `classify`, không mở thân hàm đo.
LSP có — không kế thừa; mọi nhánh của `dem_anh` trả int, mọi nhánh thiếu thư viện đều
         ném đúng `ThieuThuVienDem`.
ISP có — mọi tham số đều dùng thật; `dem_qua_venv(doan)` nhận đúng thứ nó cần.
DIP có — `token_audit` dùng lại `skill_tokens.nap_bo_dem`/`dem_qua_venv` thay vì cài
         lại loader thứ hai; hook vẫn đi qua `remind`/`echo_line` của `_common`.
```

## Kết luận

PASS toàn bộ 16 hạng mục (12 DoD + F1–F4). Đỏ duy nhất trong suite là
`test_skill_router::test_moi_duong_dan_khac_rong_deu_mo_duoc` (25 subtest, các skill
`figma-*`), đã đỏ trước request — chứng minh bằng `git stash --include-untracked`.
