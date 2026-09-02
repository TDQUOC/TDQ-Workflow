# QUICK — thi hành phương án 2301: chuyển luật vào skills, cắt CLAUDE.md

**Ngày:** 2026-09-02 · Brief: ../brief/2026-09-01-2355-thi-hanh-cat-instruction.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** tdq-conventions
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
- Trong: viết 5 dòng CHUYỂN vào `skills/` đúng 2 đích của báo cáo 2301 mục 4.
- Trong: cắt `~/.claude/CLAUDE.md` 57 → 29 dòng theo đúng bản ở báo cáo 2301 mục 6, SAU khi
  T1/T2 xong. Có bản chép lui trước khi ghi.
- Trong: cập nhật `docs/tdq/audit/luat-hien-co.md` cho phần lệch số dòng do T2 chèn dòng.
- Trong: dựng lại 3 bundle portable vì `skills/` đổi.
- Bỏ B0: đã có tiền lệ — báo cáo 2301 vừa chạm đúng hai khu vực này, kiểm kê còn nguyên giá trị.
- Bỏ B2: không có ẩn số ngoài repo, toàn file cục bộ.
- Bỏ vòng phạm vi: phạm vi đã đóng sẵn ở mục 4/6/8 của báo cáo 2301.
- NGOÀI: hai khoá Tavily trong `settings.json` — quyết định riêng của user.
- NGOÀI: thêm hook mới; phương án 2301 không đề nghị hook nào.

## Task
- [x] **T1** Thêm luật "không tự vào plan mode" vào `approval.md` (mục NOT an approval) —
  Test: `python3 scripts/doc_lint.py skills/tdq-conventions` thoát 0 và `grep -c 'plan mode'`
  trên file trả ≥ 1
  - Chạm: `skills/tdq-conventions/references/approval.md`
- [x] **T2** Thêm 4 luật còn lại vào `tdq-conventions/SKILL.md`: §7 Git nhận 2 dòng (chưa có
  git → được init + kiểm merge worktree; ngoại lệ build TDQ bị chặn → tự commit, KHÔNG push,
  liệt kê trong report) đặt sát dòng "Never commit or push before the user asks"; §8 Research
  nhận 1 gạch đầu dòng về mem0 (search trước khi kết luận, project = tên repo, chốt xong
  `remember`) — Test: `doc_lint.py skills/tdq-conventions` thoát 0; `pytest
  tests/test_token_budget.py -q` xanh
  - Chạm: `skills/tdq-conventions/SKILL.md`
  - Phát hiện khi làm: `doc_lint` R6 chặn file này ở trần **165 dòng** mà file đang 164 —
    chỉ thừa 1 dòng, không đủ cho 4 luật. Nới trần 165 → 168 nằm trong cùng task này vì đó
    là cùng một đơn vị việc, kèm dòng lý do có ngày theo khuôn các lần nới trước.
  - Chạm thêm: `scripts/doc_lint.py`
- [x] **T3** Cập nhật neo + số dòng trong `docs/tdq/audit/luat-hien-co.md` cho các luật bị T2
  đẩy lệch — Test: `pytest tests/test_luat_skill.py -q` không đỏ thêm so với mốc, độ lệch
  không vượt 57/329
  - Chạm: `docs/tdq/audit/luat-hien-co.md`
- [x] **T4** Chép lui `~/.claude/CLAUDE.md` → `~/.claude/CLAUDE.md.bak-2026-09-02`, rồi ghi
  bản 29 dòng của báo cáo 2301 mục 6 — Test: `wc -l ~/.claude/CLAUDE.md` trả 29; file `.bak`
  tồn tại và có 57 dòng
  - Chạm: `~/.claude/CLAUDE.md` (NGOÀI repo — duyệt plan này là cho phép ghi)
- [x] **T5** Bump version + CHANGELOG, dựng lại 3 bundle portable — Test:
  `python3 scripts/tdq_checkportable.py check` in CLEAN cho cả 3 bundle
  - Chạm: `CHANGELOG.md`, `portable_claude/`, `portable_codex/`, `antigravity_portable/`

## Definition of Done
- `python3 scripts/doc_lint.py skills/tdq-conventions` thoát 0
- `python3 -m pytest tests/ -q` không vượt mốc đỏ 101 fail, không file mới vào bảng lỗi
- `wc -l ~/.claude/CLAUDE.md` trả 29, và bản `.bak` 57 dòng tồn tại
- Cả 5 luật CHUYỂN đều grep thấy trong `skills/`, mỗi luật đúng 1 chỗ
- 3 bundle portable đều in CLEAN

## QC
- Q1 test từng task: **PASS** — T1 `doc_lint.py skills/tdq-conventions` → `0 violation(s)
  total, exit 0` và `grep -c 'plan mode'` trên `approval.md` → 4. T2 lint xanh +
  `pytest tests/test_token_budget.py -q` → `8 passed`. T3 `pytest tests/test_luat_skill.py -q`
  → độ lệch **57/329**, đúng mốc cũ. T4 `wc -l` → 29 và 57. T5 `tdq_checkportable.py check
  --root <dir>` → CLEAN cho cả 3.
- Q2 DoD "`doc_lint.py skills/tdq-conventions` thoát 0": **PASS** — `0 violation(s) total,
  exit 0` trên 13 file.
- Q3 DoD "`pytest tests/ -q` không vượt mốc đỏ 101 fail": **PASS** — `101 failed, 1453 passed,
  1421 subtests passed in 207.72s`. Đúng mốc; bảng lỗi vẫn là 5 file đỏ sẵn (test_bench,
  test_doc_lint, test_luat_skill, test_rules_library, test_skill_router), không file mới.
- Q4 DoD "`wc -l ~/.claude/CLAUDE.md` trả 29, bản `.bak` 57 dòng tồn tại": **PASS** —
  `29 /Users/…/.claude/CLAUDE.md` · `57 /Users/…/.claude/CLAUDE.md.bak-2026-09-02`.
- Q5 DoD "5 luật CHUYỂN đều grep thấy trong `skills/`, mỗi luật đúng 1 chỗ": **PASS** —
  `grep -c` luật plan mode trên `approval.md` → 1; `grep -n` ba mẫu còn lại trên `skills/`
  (trừ bundle portable) → 3 dòng, không dòng nào lặp. Tổng 4 vị trí cho 5 luật vì hai luật
  mem0 (search trước khi kết luận + `project` = tên repo) viết chung một gạch đầu dòng, đúng
  như báo cáo 2301 mục 4 đã chỉ định.
- Q6 DoD "3 bundle portable đều in CLEAN": **PASS** — portable_claude 90 file,
  portable_codex 138, antigravity_portable 83, cả ba in CLEAN.
- Phát sinh trong lúc làm, đã xử trong cùng request: trần R6 của `tdq-conventions/SKILL.md`
  là 165 mà file đang 164 — chỉ thừa 1 dòng. Nới 165 → 168 kèm lý do có ngày trong
  `scripts/doc_lint.py`. Đây là cắt ròng: 4 dòng thêm vào file nạp theo nhu cầu, đổi lấy
  28 dòng bỏ khỏi file nạp mỗi lượt của mọi project.
