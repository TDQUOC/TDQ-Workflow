# QC — Sửa bộ workflow TDQ chạy đủ tính năng trên Windows
Ngày: 2026-09-21 · Plan: ../plan/2026-09-20-1823-sua-tdq-chay-windows.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Máy chạy QC: Windows 11 Enterprise LTSC 2024 (10.0.26100), Python 3.13.15, Git for Windows với
`core.autocrlf=true`. Mọi lệnh dưới đây chạy thật, output dán nguyên.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Module ép UTF-8 | `discover tests -p test_utf8_io.py` | Ran 12, OK | PASS |
| Q2 | Entry point dưới cp1252 | `... -p test_utf8_io.py -k entrypoint` | Ran 2, OK | PASS |
| Q3 | Sáu hook | `... -p test_hook_windows.py` | Ran 5, OK | PASS |
| Q4 | `hooks.json` bất biến | `... -p test_sua_da_nen_tang.py` | Ran 17, OK | PASS |
| Q5 | Shim ba shell | `... -p test_shim_python3.py` | Ran 13, OK | PASS |
| Q6 | Lưới an toàn | `... -p test_ten_lenh_he.py` | Ran 11, OK | PASS |
| Q7 | Harness test | `... -p test_skill_inventory.py` | Ran 28, OK | PASS |
| Q8 | Biên xuất dấu chéo | `... -p test_kiem_no_marker.py` + `test_context_surface.py` | Ran 15 + 15, OK | PASS |
| Q9 | Kho skill-index | `... -p test_skill_router.py` | Ran 18, OK | PASS |
| Q10 | Layout `synced/` | `... -p test_skill_inventory.py -k synced` | Ran 1, OK | PASS |
| Q11 | Full suite trên Windows | `python3 -m unittest discover tests` | Ran 1983, OK, 17 skip | PASS |
| Q12 | Không ca nào xanh chuyển sang đỏ | đối chiếu với mốc đầu request | 0 fail cuối cùng | PASS |
| Q13 | Ba bundle portable | `tdq_checkportable.py check --root <bundle>` | CLEAN 104 / 156 / 94 | PASS (kèm nợ khai báo) |
| Q14 | Luật `find_references` | `... -p test_tdq_lsp_skill.py` | Ran 9, OK | PASS |
| Q15 | Lọc nhiễu lumen | `... -p test_lumenignore.py` | Ran 4, OK | PASS |
| Q16 | Phát hành | `doc_lint.py CHANGELOG.md` + đọc `plugin.json` | 0 vi phạm, 317 dòng, version 0.49.0 | PASS |
| Q17 | Lint tài liệu request | `doc_lint.py` trên brief, spec, plan | 0 vi phạm | PASS |
| QC-F1 | Toàn bộ suite | `python3 -m unittest discover tests` | Ran 1983, OK | PASS |
| QC-F2 | Hồi quy vùng đã chạm | test của từng module trong dòng `Chạm:` | xem dưới | PASS |
| QC-F3 | Ràng buộc kiến trúc | 6 kiểm, xem dưới | 6/6 giữ nguyên | PASS |
| QC-F4 | Clean code | 5 câu tự kiểm SOLID | 5/5 có | PASS |

## Bằng chứng

### Q11 và QC-F1 — toàn bộ suite

```
Ran 1983 tests in 282.724s

OK (skipped=17)
```

Mốc đầu request, cùng máy, cùng lệnh: `Ran 1907 tests · FAILED (failures=670, errors=97)` khi
chạy mặc định, và `failures=357, errors=7` khi ép `PYTHONUTF8=1`. Bản cuối không cần biến môi
trường nào.

### Q12 — không ca nào xanh chuyển sang đỏ

Lượt cuối có 0 fail và 0 error, nên mệnh đề đúng hiển nhiên. Ba ca mới bị `skip` đều đang ĐỎ
trên Windows từ trước, không phải xanh: `test_team_mode` một ca dựng tình huống bằng
`chmod(0o500)` lên thư mục, `test_codex_run` hai ca khẳng định bit quyền POSIX `0o600`/`0o700`.
Cả ba vẫn chạy bình thường trên macOS và Linux vì điều kiện skip là `sys.platform.startswith("win")`.

### Q13 — ba bundle, và một lỗi đa nền tảng có sẵn được tìm ra tại đây

Lần chạy đầu của hạng mục này ra **DRIFT gần như toàn bộ**: 104/105, 156/157, 94/95 file.
Nguyên nhân KHÔNG phải bundle cũ, mà là:

- `core.autocrlf=true` là mặc định của Git for Windows;
- `.gitattributes` của repo chỉ khai một merge driver cho `graphify-out/graph.json`, không chặn
  đổi dòng;
- manifest giữ sha256 của bytes LF, dựng trên macOS.

Nên mọi clone Windows đều thấy cả ba bundle lệch toàn bộ dù file hoàn toàn đúng. Đây là lỗi có
sẵn, không do request này sinh ra. Task `QC1.1` khai `-text` cho ba thư mục bundle, rồi lấy lại
bytes từ blob gốc. Sau khi vá:

```
  portable_claude: CLEAN    104 file(s) match the manifest
  portable_codex: CLEAN    156 file(s) match the manifest
  antigravity_portable: CLEAN    94 file(s) match the manifest
```

**Nợ đã khai, theo phán quyết `2a` của user:** ba bundle vẫn mang nội dung 0.48.0, chưa có
`scripts/utf8_io.py` và các sửa khác. Dựng lại là bước phát hành và phải chạy trên macOS hoặc
Linux, vì bản agy nướng cứng thư mục nhà của máy dựng. Lệnh: `python3 scripts/build_portable.py`.

### QC-F2 — hồi quy vùng đã chạm

Mọi đường dẫn trong các dòng `Chạm:` của plan đều nằm trong `scripts/`, `hooks/scripts/`,
`tests/` hoặc là file cấu hình ở gốc. Lượt chạy đầy đủ 1983 ca phủ trọn ba thư mục đó và xanh
hết, nên không còn vùng nào phải chạy riêng.

Hai node có sửa mà KHÔNG CÓ TEST riêng, ghi lại thành nợ kỹ thuật:

- `KHÔNG CÓ TEST: scripts/tdq_codex.boc_lenh` — nhánh `.cmd` chỉ chạy trên Windows và được phủ
  gián tiếp qua `test_codex_cli` (32 ca xanh), nhưng bản thân hàm chưa có ca kiểm trực tiếp cho
  nhánh POSIX.
- `KHÔNG CÓ TEST: scripts/tdq_state.xoa_cay` — được phủ gián tiếp qua `test_claude_export` và
  `test_bench`, chưa có ca kiểm riêng cho nhánh chọn `onexc` so với `onerror` theo phiên bản
  Python.

### QC-F3 — ràng buộc kiến trúc trong spec §5

| Ràng buộc | Cách kiểm | Kết quả |
|---|---|---|
| `scripts/` không được import `hooks/` | grep `import hooks` trong `scripts/*.py` | 0 chỗ |
| File code mới phải nằm trong `scripts/` hoặc `hooks/` | `scripts/utf8_io.py` | đúng chỗ |
| `skills/` chỉ nhắc tên lệnh, không chép thân script | request này không sửa chuỗi lệnh nào trong `skills/` | giữ nguyên |
| Chú thích, docstring và chuỗi máy viết tiếng Anh | `i18n_check.py` trên `utf8_io.py` và `tdq_ten_lenh.py` | 0 dòng tiếng Việt |
| Chỉ `tdq_state.py` được ghi `state.json` | grep chỗ ghi ngoài `tdq_state.py` | 0 chỗ ghi |
| `CHANGELOG.md` dưới trần 500 dòng | `wc -l` | 317 dòng |

### QC-F4 — clean code, 5 câu SOLID

- **SRP** — có. `utf8_io` chỉ đổi encoding luồng ra; `ten_lenh_python` chỉ trả tên lệnh;
  `boc_lenh` chỉ dựng tiền tố argv; `xoa_cay` chỉ xoá cây thư mục. Mỗi hàm một lý do để đổi.
- **OCP** — có. Thêm một thư mục tạm cần bỏ qua là thêm một phần tử vào `THU_MUC_TAM`; thêm một
  đuôi cần bọc qua shell là thêm vào tuple trong `boc_lenh`; không phải mở thân hàm nào.
- **LSP** — có. Không dùng kế thừa. Mọi nhánh `return` của `force_utf8` trả `int`, của
  `can_nhac_ten_lenh` trả `str` (rỗng thay vì `None`), của `cai_shim_python3` trả đúng cặp
  `(list, list)` ở cả nhánh từ chối lẫn nhánh ghi.
- **ISP** — có. Mọi tham số đều được dùng; các tham số tiêm (`tim_lenh`, `ghi_duoc`, `ghi_file`,
  `nen_tang`, `chuoi_path`) tồn tại để kiểm được nhánh Windows từ máy khác, và đều có đường
  chạy thật trong test.
- **DIP** — có, và đây là chỗ đã sửa trong lúc làm: `ten_lenh_python` ban đầu là bản chép thứ hai
  của `build_portable.tien_to_python`. Đã dời nguồn sự thật sang `tdq_ten_lenh.py` và cho
  `build_portable` gọi lại, nên năm chỗ gọi cũ cộng một chỗ mới ở tầng hook đọc cùng một hằng.

### Hợp đồng skill — `tdq-lean` (dòng `Dùng:` của T2.3)

Nhận xét soi over-engineer, đúng thứ mà `Ra` của hợp đồng đòi:

Cơ chế shim **không làm quá tay**, và chính việc soi đã cắt bớt được ba thứ:

1. **Bỏ hẳn việc sửa 96 chuỗi trong `skills/`.** Bản spec 1.0 định đổi chúng sang placeholder;
   soi lại thì cách đó vừa không khả thi (hook không rewrite được file model đọc) vừa thừa, vì
   hai file shim một dòng giải quyết trọn vẹn. Tầng luật không bị đụng một chữ.
2. **Bỏ việc sinh lại `hooks.json` theo hệ.** Khi shim đã làm `python3` thành lệnh thật, file
   giữ nguyên `python3` cho cả ba hệ — hết diff bẩn, hết bước cài thủ công.
3. **Không viết lại `tien_to_python`.** Hàm đã có sẵn kèm 17 ca test; chỉ dời chỗ cho hook dùng
   được, theo bậc 2 của luật "build less than asked".

Chỗ duy nhất đáng ngờ là `THU_MUC_TAM`: nó đoán trước `nvm_multishells` dù máy này chỉ có `fnm`.
Giữ lại vì `nvm4w` dùng đúng cơ chế symlink theo shell, và cái giá là một chuỗi trong frozenset.

Lệnh kiểm của hợp đồng: `python3 scripts/doc_lint.py docs/tdq/qc/2026-09-20-1823-sua-tdq-chay-windows.md`.

## Kết luận

PASS toàn bộ: 17/17 hạng mục DoD và 4/4 hạng mục cố định.

Một vòng fix (`QC1.1`) đã chạy, vá lỗi line-ending làm hỏng phép kiểm bundle trên mọi máy
Windows. Hai món nợ kỹ thuật được khai ở QC-F2 và một món ở Q13, tất cả đưa vào report.
