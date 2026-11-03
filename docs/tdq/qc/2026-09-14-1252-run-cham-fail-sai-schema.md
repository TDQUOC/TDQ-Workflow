# QC — `run` chấm fail dù Codex làm đúng (rào code quanh JSON)
Ngày: 2026-09-14 · Plan: ../plan/2026-09-14-1252-run-cham-fail-sai-schema.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | 5 dạng được nhận ra dict | `… -p "test_codex_run.py" -k DocKetQuaRaoTest` | 3 test OK (5 subTest nhận) | PASS |
| Q2 | 9 dạng bị từ chối + file thiếu | cùng lệnh Q1 | 10 subTest từ chối ra `None` | PASS |
| Q3 | chỉ `xong` = `true` là xong | `… -k PhanQuyetLyDoTest` | `false`/`"true"`/`1`/`null`/thiếu khoá đều `fail` | PASS |
| Q4 | mã lý do tập đóng, `PhanQuyetTest` cũ xanh không sửa | `… -k PhanQuyet` | 10 test OK (5 mới + 5 cũ `PhanQuyetTest`, không test cũ nào bị xoá/sửa; plan ghi nhầm "6 test cũ") | PASS |
| Q5 | schema có `additionalProperties: false` | `… -k KhuonSchemaTest` | 2 test OK; `schema.json` thật của Q10 có khoá này | PASS |
| Q6 | dòng log mang `ly_do`, tắt được bằng `TDQ_LOG=0` | `… -k LogTest` | 9 test OK | PASS |
| Q7 | bench đọc đúng dòng log mới | `… -p "test_bench.py" -k LogCodexTest` | 6 test OK | PASS |
| Q8 | `codex-mode.md` cập nhật, không lỗi mới | `i18n_check.py` · `doc_lint.py` · `grep -c` | exit 0 · 0 vi phạm · 2 | PASS |
| Q9 | bundle khớp nguồn | `build_portable.py` · `-p "test_build_portable.py"` · `cmp` | 61 test OK; 6/7 bản giống hệt, bản Antigravity khác đúng thiết kế | PASS |
| Q10 | lượt thật làm được ra `xong` | `tdq_codex.py run Q10 …` | `xong`, exit 0, vùng file đạt | PASS |
| Q11 | lượt thật không làm được ra ≠ `xong` kèm `ly_do` | `tdq_codex.py run Q11 …` | `fail`, exit 1, `ly_do=model-bao-chua-xong` | PASS |
| Q12 | không hồi quy | bộ đầy đủ + mốc đo lại trên worktree HEAD | 3 fail thêm do sổ lượt thật của workflow, không do thay đổi này | PASS |
| QC-F1 | cả bộ test | `env -u TDQ_LOG python3 -m unittest discover tests` | 1785 test · 293 fail / 4 error · mốc HEAD 1771 test · 290/4 | PASS |
| QC-F2 | vùng chạm | test module của từng nút `Chạm:` | 54 + 46 + 61 OK · KHÔNG CÓ TEST: `_cli_run` | PASS có nợ |
| QC-F3 | ràng buộc kiến trúc | xem bằng chứng | 3/3 dòng giữ | PASS |
| QC-F4 | clean code | 5 câu tự kiểm | 5/5 có | PASS |

## Bằng chứng

### Q1–Q7 (test đơn vị, lệnh dạng `env -u TDQ_LOG python3 -m unittest discover tests -p "<file>" -k <lớp>`)
```
DocKetQuaRaoTest (đỏ trước khi sửa): FAILED (failures=4) — 4 dạng có rào ra None
DocKetQuaRaoTest + PhanQuyetTest (xanh): Ran 8 tests · OK
PhanQuyetLyDoTest (đỏ): FAILED (errors=5) — chưa có MA_LY_DO/phan_quyet_ly_do
-k PhanQuyet + DocKetQuaRaoTest (xanh): Ran 13 tests · OK
chạy lại lúc QC: DocKetQuaRaoTest Ran 3 · PhanQuyetLyDoTest Ran 5 · PhanQuyet Ran 10 · KhuonSchemaTest Ran 2 · LogTest Ran 9 · LogCodexTest Ran 6 — tất cả OK
git diff HEAD -- tests/test_codex_run.py | grep "^-.*def test_" → rỗng (không test cũ nào bị xoá/sửa tên)
KhuonSchemaTest: đỏ FAILED (errors=2) → xanh Ran 2 tests · OK
LogTest: đỏ FAILED (errors=2) → sau T4.1: test_codex_run.py toàn file Ran 54 tests · OK
LogCodexTest: Ran 6 tests · OK — trên bản HEAD của tdq_codex.py lời gọi mới báo
  TypeError: dong_log_luot() takes 6 positional arguments but 7 were given
```

### Q8
```
i18n_check: done — 0 line(s), exit 0
doc_lint: done — 0 violation(s) total, exit 0
grep -c "rào code\|code fence" → 2
```

### Q9
```
trước build: DIFF ở cả 7 bản sao tdq_codex.py / codex-mode.md
sau build: same ×6 · DIFF antigravity_portable/skills/tdq-build/references/codex-mode.md
  → chỉ khác đường dẫn `scripts/…` được viết lại thành `~/.gemini/config/plugins/tdq-workflow/scripts/…`;
    bản HEAD cũng khác nguồn HEAD đúng kiểu này (thiết kế của build_portable)
test_build_portable.py: Ran 61 tests · OK
portable_codex.zip: không script/test nào sinh hay đọc; commit cuối a107c55 (0.24.0); không chứa tdq_codex.py → không cần sinh lại
```

### Q10 — lượt thật, model `ag/gemini-3.8-flash-medium`
```
exit=0
{"trang_thai": "xong", "giay": 27.1, "vung_file": {"dat": true, "lech": [], "khoa_bi_cham": []}}
[2026-09-14T13:30:03+07:00] luot Q10 · model=ag/gemini-3.8-flash-medium · home=…/tdq-codex-home-2pm47dzr · 27.1s · xong · sha256=c58131f70b413b3a · dau="Nhiệm vụ: tạo file docs/tdq/qc/q10-probe"
ket-qua.json: {"xong": true}
schema.json: {"type": "object", "properties": {"xong": {"type": "boolean"}}, "required": ["xong"], "additionalProperties": false}
docs/tdq/qc/q10-probe.txt: Q10-OK
grep -c -e Bearer -e sk- (stdout, stderr): 0, 0
```

### Q11 — lượt thật, task không thể làm, `--vung` rỗng
```
exit=1
{"trang_thai": "fail", "giay": 61.4, "vung_file": {"dat": true, "lech": [], "khoa_bi_cham": []}}
[2026-09-14T13:31:20+07:00] luot Q11 · model=ag/gemini-3.8-flash-medium · home=…/tdq-codex-home-5n13zzja · 61.4s · fail · sha256=fb62d5e4a75ec43b · dau="Nhiệm vụ: làm cho lệnh `false` thoát với" · ly_do=model-bao-chua-xong
ket-qua.json: {"xong": false}
grep -c -e Bearer -e sk- (stdout, stderr): 0, 0
dọn: rm docs/tdq/qc/q10-probe.txt · tdq_codex.py cleanup → "deleted 2 temporary CODEX_HOME(s)" · .tdq-codex-home không còn
```
Trước bản sửa, `{"xong": false}` bị chấm `xong` (chỉ kiểm có khoá); nay ra `fail` kèm lý do.

### Q12 / QC-F1 — hồi quy
```
nhánh:  Ran 1785 tests in 107.269s · FAILED (failures=293, errors=4, skipped=14)
HEAD (worktree tách rời, đo cùng lúc): Ran 1771 tests in 107.744s · FAILED (failures=290, errors=4, skipped=15)
chỉ có ở nhánh: 3 FAIL test_codex_edit_gate.TestChanNgoaiVung
  (test_trong_vung_thi_khong_chan[apply_patch], test_vung_la_thu_muc_thi_file_ben_trong_duoc_ghi,
   test_duong_tuyet_doi_trong_repo_quy_ve_duong_tuong_doi) · chỉ có ở HEAD: không có
lý do hook trả: "[TDQ:TICK] 3 edits in a row with no tick in the plan — close the task before editing on."
cơ chế: codex_edit_gate.py gọi edit_gate.py; edit_gate.py đếm dòng code_edit trong sổ lượt THẬT của repo theo
  checksum plan, chặn từ lượt 3 khi phase implement/qc. Worktree HEAD không có docs/tdq/state.json (gitignore) nên không chặn.
git diff --quiet HEAD -- hooks/ tests/test_codex_edit_gate.py → không đổi
thí nghiệm quyết định (ngay sau khi plan đổi checksum): run 1: OK · run 2: FAILED (failures=3)
test_codex_*.py: Ran 104 tests · OK · test_bench.py: Ran 46 tests · OK
```

### QC-F2 — vùng chạm
```
doc_ket_qua, phan_quyet, dong_log_luot, khuon_schema, in_log_luot → test_codex_run.py: Ran 54 tests · OK
doc_log_codex (chỉ đọc) → test_bench.py: Ran 46 tests · OK
bundle → test_build_portable.py: Ran 61 tests · OK
KHÔNG CÓ TEST: _cli_run (không có test đơn vị đầu-cuối; chỉ được phủ bằng lượt thật Q10/Q11)
```

### QC-F3 — ràng buộc kiến trúc (spec §5)
```
1. skills chỉ nhắc tên lệnh: codex-mode.md chỉ nhắc `MA_LY_DO` trong `scripts/tdq_codex.py`, luật đọc mô tả bằng lời, không chép code/regex → giữ
2. docstring/chú thích/chuỗi máy tiếng Anh: i18n_check scripts/tdq_codex.py → 0 line(s), exit 0; mã lý do là định danh không dấu → giữ
3. bản ngoài sinh bằng build_portable.py, không sửa tay → giữ (Q9)
```

### QC-F4 — clean code (5 câu tự kiểm)
```
SRP có: _boc_rao chỉ bóc rào · doc_ket_qua_ly_do chỉ đọc file · _ly_do_ket_qua chỉ xét nội dung · phan_quyet_ly_do chỉ xếp thứ tự bằng chứng · in_log_luot chỉ in theo công tắc
OCP có: tên mã là dữ liệu trong MA_LY_DO; tập mã ĐÓNG theo spec, thêm mã mới là đổi hợp đồng chứ không phải mở rộng
LSP có: mọi nhánh return cùng kiểu — doc_ket_qua_ly_do/phan_quyet_ly_do luôn trả cặp, _ly_do_ket_qua trả str hoặc None, _boc_rao luôn trả str
ISP có: mọi tham số mới (ly_do, ly_do_doc) đều được dùng
DIP có: dùng lại _log_enabled (công tắc TDQ_LOG) và mask_secrets; phan_quyet/doc_ket_qua cũ gọi lại hàm mới, không nhân đôi luật
ruff: CHƯA KIỂM — ruff không có trên máy (python3 -m ruff: No module named ruff)
```

## Kết luận
PASS toàn bộ 12 mục DoD + 4 mục cố định. Nợ kỹ thuật nêu ở report: `_cli_run` chưa có test đơn vị đầu-cuối;
`test_codex_edit_gate` gọi hook thật vào sổ lượt của repo nên đỏ khi repo đang implement/qc (ngoài phạm vi).
