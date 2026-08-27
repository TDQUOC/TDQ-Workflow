# QC — bundle portable cho Antigravity CLI (agy)
Ngày: 2026-08-27 · Plan: ../plan/2026-08-27-1112-antigravity-portable-skill.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bundle agy sinh độc lập, không đụng 2 bundle kia | `build_portable.py --only antigravity` + so sha toàn cây | sha trước = sau, byte-identical | PASS |
| Q2 | `PreToolUse` deny đúng case, allow lệnh hợp lệ | `pytest tests/test_agy_hooks.py -q -k PreToolUse` | 15 passed | PASS |
| Q3 | `Stop` chặn đúng 3 điều kiện port từ `stop_gate.py` | `pytest tests/test_agy_hooks.py -q -k Stop` | 10 passed | PASS |
| Q4 | Cấu hình JSON hợp lệ, không lộ secret | `pytest tests/test_build_portable.py -q -k Antigravity` | 11 passed | PASS |
| Q5 | Đã dọn 3 chỗ mô tả Antigravity là fallback markdown | `grep -n Antigravity` 3 file | 0 dòng còn mô tả fallback | PASS |
| Q6 | Bộ test tổng | `python3 -m pytest tests/ -q` | 1579 passed, 5 FAILED — cả 5 CÓ TỪ TRƯỚC | PASS có ghi chú |
| Q7 | Hồi quy Hub `main()` (`--only claude` / `--only codex`) | 2 lệnh + so sha | exit 0, cây không đổi 1 byte | PASS |
| QC-F1 | Bộ test tổng theo lệnh trong plan | như Q6 | như Q6 | PASS có ghi chú |
| QC-F2 | Regression vùng `Chạm:` | `pytest` 6 file test của hooks + build_portable + checkportable | 248 passed, 53 subtests | PASS |
| QC-F3 | 4 ràng buộc kiến trúc spec §5 | xem Bằng chứng | cả 4 giữ nguyên | PASS |
| QC-F4 | Clean code 5 câu tự kiểm | xem Bằng chứng | 5/5 "có" | PASS |

## Bằng chứng

### Q1 + Q7
```
before=ac517123d425991204c4d3ae472f9a2bdbc03b66
after =ac517123d425991204c4d3ae472f9a2bdbc03b66   → Q1 PASS: byte-identical
--only claude exit=0 · --only codex exit=0 · regen idempotent: PASS
```
Lỗi rò đã sửa trong lúc QC-nội-bộ của P2: 2 file hook agy từng lọt sang `portable_claude/`
và `portable_codex/` (cả 2 hàm sinh copy nguyên thư mục `hooks/`). Sửa bằng
`copy_loc(..., bo_qua_them=FILE_HOOK_AGY)` — KHÔNG đưa vào `EXCLUDE_FILES` vì set đó dùng
chung cho `sinh_manifest`, để vào đó thì bundle agy sẽ chứa 2 file không được manifest liệt kê.

### Q2 / Q3 / Q4
```
15 passed, 11 deselected     (PreToolUse)
10 passed, 16 deselected     (Stop)
11 passed, 42 deselected     (Antigravity trong test_build_portable)
```

### Q5
4 dòng "Antigravity" còn lại đều là của chính bundle agy (README_AGY, docstring
`sinh_ban_antigravity`, description hooks.json, dòng mô tả target mới trong docstring đầu file).
`portable_codex/README.md` và `AGENTS.md`: 0 dòng.

### Q6 — 5 lỗi CÓ TỪ TRƯỚC, không do request này
Chứng minh bằng worktree sạch tại HEAD (`git worktree add /tmp/tdq-base HEAD`):
```
FAILED tests/test_bench.py::…test_repo_that_khong_moc_nhanh_hay_worktree_nao   ← fail tại HEAD
FAILED tests/test_luat_skill.py::…test_so_dong_ghi_trong_bang_van_tro_dung_cho ← fail tại HEAD
FAILED tests/test_skill_router.py::…test_so_ban_ghi_khop_skill_inventory       ← fail tại HEAD
FAILED tests/test_doc_lint.py::…test_repo_docs_clean   ← 2 câu dài ở skills/tdq-build/SKILL.md
                                  và skills/tdq-lsp-setup/… , cả 2 file `git diff` rỗng
FAILED tests/test_rules_library.py::ChiMuc::test_chi_muc ← do sửa đổi CHƯA COMMIT có sẵn ở
                                  skills/tdq-build/references/rules/index.md (thêm dòng
                                  `bash.md` nhưng chưa có file rule) — có trong git status
                                  ngay từ đầu phiên, trước mọi thay đổi của request này
```
Một lỗi THỰC SỰ do request này gây ra đã được sửa trong QC: `test_compliance_protocol.py::
test_no_transcript_no_deny` cấm mọi hook tự dựng JSON `deny` ngoài `_common.block()`. Bất biến
đó là của harness Claude Code; deny cứng của agy chính là mục tiêu spec §1. Đã nới danh sách
cho phép đúng 2 file agy-only kèm comment giải thích → `test_compliance_protocol.py`: 16 passed.

### QC-F3 — 4 ràng buộc kiến trúc
```
A1 scripts/ không import hooks/   → grep 'import hooks' scripts/build_portable.py = 0 dòng (chỉ shutil.copy2)
A2 skills/ chỉ nhắc tên lệnh      → nội dung skill port giữ nguyên bản nguồn; chỉ đổi đường dẫn
                                     tương đối thành absolute; các đoạn `def …` duy nhất là VÍ DỤ
                                     code trong rules/python.md, có sẵn từ bản nguồn
A3 chỉ tdq_state.py ghi state     → hook deny thật: {"decision":"deny","reason":"[TDQ:STATE] …"}
A4 deny không dùng cho 'chưa duyệt' → grep 'approved' trong agy_pretooluse_gate.py = 1 dòng, và là
                                     dòng docstring nói rõ KHÔNG dùng deny cho lý do chưa duyệt
```

### QC-F4 — clean code (file code đã sửa: `scripts/build_portable.py`, 2 hook agy mới)
```
1. Tên nói đúng việc?          có — sinh_ban_antigravity / _sua_duong_dan_tuong_doi_agy / FILE_HOOK_AGY
2. Hàm làm đúng một việc?      có — mỗi _sinh_* sinh đúng 1 file cấu hình
3. Không lặp code?             có — dùng lại copy_loc/ghi_manifest/sinh_mcp của 2 bundle cũ
4. Xử lý lỗi rõ?               có — hook fail-open khi parse lỗi; sinh_ban_* raise nếu còn biến plugin
5. Không có placeholder?       có — grep TODO|FIXME = 0
```
Log service: bật mặc định, có timestamp, tắt bằng `TDQ_LOG=0` (stderr = 0 byte khi tắt).

## Kết luận
PASS toàn bộ 7 hạng mục DoD + 4 hạng mục cố định. 5 lỗi còn lại của `pytest tests/ -q` đều có
từ trước request này, đã chứng minh bằng worktree sạch tại HEAD hoặc bằng `git diff` rỗng trên
file bị flag — nêu lại trong report như nợ kỹ thuật của repo, không thuộc phạm vi việc này.
Giới hạn phải nêu trong report: chưa test end-to-end trên agy thật (spec §5, rủi ro 4).
