# QC — Sai khuôn lấy test làm chuẩn
Ngày: 2026-09-14 · Plan: ../plan/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Tập 2 mã cứu được ⊂ `MA_LY_DO` | `unittest -p test_codex_run.py -k ChayLaiTestTest` | Ran 3 · OK | PASS |
| Q2 | Hàm quyết định mọi ca trạng thái × vùng | cùng lệnh Q1 | Ran 3 · OK | PASS |
| Q3 | Khuôn JSON 5 khoá, `ly_do` null khi `xong` | `unittest -p test_codex_run.py -k PhanQuyetJsonTest` | Ran 6 · OK | PASS |
| Q4 | Đầu-cuối `_cli_run`, không đọc `~/.codex` thật | `unittest -p test_codex_cli.py -k RunDauCuoiTest` | Ran 8 · OK | PASS |
| Q5 | Luật + checklist, không lỗi i18n/lint mới | `i18n_check.py codex-mode.md tdq_state.py` nhánh vs HEAD · `doc_lint.py codex-mode.md` | 7 dòng = 7 dòng HEAD, trùng từng dòng · lint 0 | PASS |
| Q6 | Bundle khớp nguồn | `build_portable.py` · `unittest -p test_build_portable.py` · `diff` bản sao | build 0 · Ran 61 OK · lệch = đúng số viết lại đường dẫn ở HEAD | PASS |
| Q7 | Lượt thật làm được ra `xong` | `tdq_codex.py run Q7 …` | `xong` · 5 khoá · `null` · `false` · 35.8s | PASS |
| Q8 | Lượt thật sai khuôn được cứu bằng test | `tdq_codex.py run Q8 …` + `grep -qx Q8-OK …` | `fail` · `ket-qua-sai-khuon` · `true` ở lượt 1 · test chạy lại xanh | PASS |
| Q9 | Không hồi quy | `unittest discover tests` nhánh vs worktree HEAD | 1802 · 290 fail · 4 error vs 1785 · 291 · 4 · 0 fail/error chỉ ở nhánh | PASS |
| Q10 | 0.47.0, CHANGELOG ≤ 500, merge không push | `doc_lint.py CHANGELOG.md` · `grep '"version"'` · `wc -l` | lint 0 · 3 manifest 0.47.0 · 492 dòng · merge ở bước 11 report | PASS |
| QC-F1 | Toàn bộ test | `env -u TDQ_LOG python3 -m unittest discover tests` | như Q9 | PASS |
| QC-F2 | Hồi quy vùng chạm | test module của mọi dòng `Chạm:` | 121 + 56 + 4 + 61 + 64 + 3 OK | PASS |
| QC-F3 | Ràng buộc kiến trúc §5 | 4 lệnh kiểm, xem bằng chứng | 4/4 giữ nguyên | PASS |
| QC-F4 | Clean code | 5 câu tự kiểm | 5/5 có | PASS |

## Bằng chứng

### Q1–Q4
```
== test_codex_run.py -k ChayLaiTestTest: Ran 3 tests in 0.000s OK
== test_codex_run.py -k PhanQuyetJsonTest: Ran 6 tests in 0.000s OK
== test_codex_cli.py -k RunDauCuoiTest: Ran 8 tests in 4.589s OK
```
`RunDauCuoiTest` dựng `HOME` và `CODEX_HOME` trong thư mục tạm, Codex giả trên `PATH`; ca
`test_codex_chi_thay_home_tam_mang_config_gia` khẳng định `config.toml` Codex thấy là bản giả. Đỏ đã thấy trên worktree
HEAD: `AssertionError: Lists differ: ['trang_thai', 'giay', 'vung_file'] != [… 'ly_do', 'can_chay_lai_test']`.

### Q5
```
== nhánh: 7 Vietnamese line(s) in 2 file(s) · exit=1
== HEAD : 7 Vietnamese line(s) in 2 file(s) · exit=1
(cùng 7 dòng: tdq_state.py:163, 164, 202, 1094, 1235, 1236, 1237 — có sẵn từ trước)
doc_lint codex-mode.md: 0 violation(s) total, exit 0
grep -c can_chay_lai_test codex-mode.md = 4 · grep -c "cứu bằng test" = 2 · test_luat_mode Ran 4 OK
```

### Q6
```
build=0 · test_build_portable: Ran 61 tests OK
tdq_codex.py   : portable_claude 0 · portable_codex 0 · antigravity_portable 0
tdq_state.py   : 2 · 2 · 2   (dòng `_SCRIPT_PATH.sub` viết lại đường dẫn — HEAD cũng 2)
codex-mode.md  : portable_claude 0 · portable_codex (.agents + workflow) 0 · 0 · antigravity 8
                 (đường dẫn ~/.gemini/config/plugins/tdq-workflow/scripts/ — HEAD cũng 8)
```

### Q7
```
red: q7-probe.txt chưa có
exit=0
{"trang_thai": "xong", "giay": 35.8, "vung_file": {"dat": true, "lech": [], "khoa_bi_cham": []}, "ly_do": null, "can_chay_lai_test": false}
luot Q7 · model=ag/gemini-3.8-flash-medium · 35.8s · xong · sha256=892bb6ea997dc5c4
test Q7 xanh · soát Bearer/sk- = 0
```

### Q8
```
red: q8-probe.txt chưa có
luot 1 exit=1
{"trang_thai": "fail", "giay": 11.4, "vung_file": {"dat": true, "lech": [], "khoa_bi_cham": []}, "ly_do": "ket-qua-sai-khuon", "can_chay_lai_test": true}
luot Q8 · model=ag/gemini-3.8-flash-medium · 11.4s · fail · sha256=d2dae4d0d363a326 · ly_do=ket-qua-sai-khuon
tái hiện ở lượt 1 · soát Bearer/sk- = 0
leader chạy lại test Q8: xanh
```
Dọn: xoá `q7-probe.txt`, `q8-probe.txt`; `tdq_codex.py cleanup: deleted 2 temporary CODEX_HOME(s)`,
thư mục home tạm còn 0 mục.

### Q9
```
nhánh (sau T5.1): Ran 1802 tests in 116.799s · FAILED (failures=290, errors=4, skipped=14)
HEAD (worktree tách rời 293c2c9): Ran 1785 tests in 121.107s · FAILED (failures=291, errors=4, skipped=15)
== chỉ có ở nhánh (so HEAD)
(trống)
== chỉ có ở HEAD
FAIL: test_thuc_do_khong_de_lai_worktree_hay_thu_muc_tam (test_bench.ThucDoTest…)
```
Lượt nhánh trước T5 lệch 3 test `test_codex_edit_gate.TestChanNgoaiVung`; chạy riêng module: nhánh
Ran 6 OK, HEAD Ran 6 OK, diff không chạm `hooks/` hay file test đó — lệch do thứ tự chạy, lượt cuối
không tái hiện. Module: `test_codex_*` Ran 121 OK · `test_bench` Ran 46 OK · `test_state` Ran 56 OK.

### Q10
```
.claude-plugin/plugin.json:4:  "version": "0.47.0",
antigravity_portable/plugin.json:4:  "version": "0.47.0"
portable_codex/manifest.json:164:  "version": "0.47.0"
492 CHANGELOG.md · doc_lint CHANGELOG.md CHANGELOG-archive.md: 0 violation(s), exit 0
grep -c "^## 0.26.0" CHANGELOG.md = 0 · CHANGELOG-archive.md = 1
test_claude_export Ran 64 OK · test_docs_consistency Ran 3 OK
```

### QC-F2
Không có nút nào thiếu test. `scripts/tdq_codex.py` → `test_codex_run`/`test_codex_cli` ·
`scripts/tdq_state.py` → `test_state` · `codex-mode.md` → `test_luat_mode` · bundle →
`test_build_portable`, `test_claude_export` · `CHANGELOG*.md` → `test_docs_consistency`.

### QC-F3
- `skills/` chỉ nhắc tên lệnh: `grep -cE "^\s*(def |return |import )" codex-mode.md` = 0.
- Chú thích `scripts/` tiếng Anh: `i18n_check scripts/tdq_codex.py` nhánh 0 = HEAD 0; `tdq_state.py` 7 = HEAD 7.
- Bundle sinh bằng `build_portable.py`: build=0, lệch bản sao đúng số của HEAD (Q6).
- `CHANGELOG.md` dưới trần 500: 492 dòng, doc_lint 0.

### QC-F4
- SRP — có: `can_chay_lai_test` chỉ quyết định, `dung_phan_quyet` chỉ dựng dòng phán quyết.
- OCP — có: thêm mã cứu được là thêm một phần tử vào `MA_LY_DO_CHAY_LAI_TEST`.
- LSP — có: `can_chay_lai_test` luôn trả `bool`, `dung_phan_quyet` luôn trả dict 5 khoá.
- ISP — có: mọi tham số của 2 hàm mới đều được dùng.
- DIP — có: vùng file đi qua `tdq_vungfile.hau_kiem`, dòng log đi qua `dong_log_luot` sẵn có.
Soát diff: TODO/FIXME mới = 0; secret (`Bearer`, `sk-`, `tvly-`) trong diff + brief/spec/plan = 0.

## Kết luận
PASS toàn bộ — 10/10 mục DoD và 4/4 mục cố định, không cần vòng fix.
